# import python functionalities
import json
from pathlib import Path
from datetime import datetime, date

# import the necessary ehrQL functionalities and tables
from ehrql import create_measures, years, case, when, months, get_parameter
from ehrql.measures import INTERVAL
from ehrql.tables.tpp import patients, clinical_events, medications, ons_deaths, practice_registrations

# import variables which are defined in a separate file
from variable_lib import (
    has_prior_event,
    has_prior_meds
)
# import the codelists defined in a separate file
import codelists

# import study dates defined in "./analysis/design/study-dates.R" script and then exported
study_dates = json.loads(
  Path("analysis/design/study-dates.json").read_text(),
)

# define start of follow up period
index_date = datetime.strptime(study_dates[get_parameter(name="period")[0]], "%Y-%m-%d").date() 

# define the patients who have were registered on index date
registered_patients = (
    practice_registrations.exists_for_patient_on(index_date)
)

# define the patients who are of the correct age
age_of_interest = (
    (patients.age_on(index_date) >= 12) & (patients.age_on(index_date) <= 100)
)

# define the patients with known sex
sex_known = patients.sex.is_in(["female", "male", "intersex"]) 

# define patients status: alive/dead: use ONS record if present, otherwise use GP record
death_date = ons_deaths.date.when_null_then(patients.date_of_death)
was_alive = death_date.is_after(index_date) | death_date.is_null()

# define the interevals to be used for the measures
if index_date == date(2020, 3, 1) :
    intervals_years = years(2).starting_on(index_date)
    intervals_months = months(24).starting_on(index_date)
else :
    intervals_years = years(3).starting_on(index_date)
    intervals_months = months(36).starting_on(index_date) 

# create ehrQL measures object for configuration
measures = create_measures()

# define the size of a dummy population
measures.configure_dummy_data(population_size = 250)

# define medication date to find recent prescriptions
medication_date = index_date - years(1)

# create combined asthma medications codelist
asthma_meds = (
    codelists.asthma_oral_medications + # oral medications
    codelists.asthma_inhaled_medications # inhaled medications
)

# identify whether patient is asthmatic
has_asthma = (
    # has a diagnosis code
    (has_prior_event(codelists.asthma_codelist, index_date))
    # and has been prescribed medications in year prior to index
    & (has_prior_meds(
        asthma_meds,
        index_date,
        where = medications.date.is_on_or_between(medication_date, index_date)
    ))
)

# identify patients diagnosed with asthma in interval
diagnosed_with_asthma = (
    clinical_events.where(clinical_events.snomedct_code.is_in(codelists.asthma_codelist))
    .where(clinical_events.date.is_during(INTERVAL))
    .exists_for_patient()
)

# get the age of particpants
age = patients.age_on(index_date)

# classify ages
age_group = (case(
    when((age >= 12) & (age < 18)).then("adolescent"),
    when((age >= 18) & (age < 60)).then("adult"),
    when((age >= 60) & (age <= 100)).then("older_adult")
))

# define default denominator
denominator = (
    registered_patients
    & age_of_interest
    & sex_known
    & was_alive
    # additional check for registration at start of every interval to remove those 
    # who deregistered DURING a previous interval
    & practice_registrations.exists_for_patient_on(INTERVAL.start_date)
)
measures.define_defaults(
    denominator = denominator
)

## yearly measures

# define the measure of interest: those with asthma, by age group
measures.define_measure(
    "measure_had_prescription_by_age_yearly",
    numerator = has_asthma,
    group_by = {"age_group": age_group},
    intervals = intervals_years,
)

## monthly measures

# define the measure of interest: monthly incident asthma, by age group
measures.define_measure(
    "measure_had_incident_asthma_by_age_monthly",
    numerator = diagnosed_with_asthma,
    group_by = {"age_group": age_group},
    intervals = intervals_months,
)
