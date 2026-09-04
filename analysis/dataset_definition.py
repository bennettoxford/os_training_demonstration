# import python functionalities
import json
from pathlib import Path
from datetime import datetime, date

# import the necessary ehrQL functionalities and tables
from ehrql import (
    create_dataset,
    months,
    years,
    case,
    when,
    minimum_of,
    get_parameter
)
from ehrql.tables.tpp import (
    patients, 
    medications,
    clinical_events,
    ons_deaths,
    practice_registrations,
    addresses
)

# import the codelists defined in a separate file
import codelists 

# create ehrQL generated dummy dataset
dataset = create_dataset() 

# import study dates defined in "./analysis/design/study-dates.R" script and then exported
study_dates = json.loads(
  Path("analysis/design/study-dates.json").read_text(),
)

# define start of follow up period
index_date = datetime.strptime(study_dates[get_parameter(name="period")[0]], "%Y-%m-%d").date()

# define end of follow up period
end_date = datetime.strptime(study_dates[get_parameter(name="period")[1]], "%Y-%m-%d").date()

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

# define the population of interest for study
dataset.define_population(
    registered_patients
    & age_of_interest
    & sex_known
    & was_alive
)

# configure the dummy data
dataset.configure_dummy_data(
    # requiring 250 patients matching the above define_population constraints
    population_size = 250
)

## define patient characteristics to extract

# age at start of follow up
dataset.age = patients.age_on(index_date) 

# sex
dataset.sex = patients.sex 

# patient ethnicity (5 groups from 2001 census)
dataset.latest_ethnicity_group = (
    clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity_codes))
    .where(clinical_events.date.is_on_or_before(index_date))
    .sort_by(clinical_events.date)
    .last_for_patient().snomedct_code
    .to_category(codelists.ethnicity_codes)
)

# patient IMD - from the LSOA associated with their address
dataset.imd_quintile = addresses.for_patient_on(index_date).imd_quintile

## get information for censoring

# date of death
dataset.death_date = (case(
    when(ons_deaths.date.is_not_null())
    .then(ons_deaths.date),
    when((ons_deaths.date.is_null()) & (patients.date_of_death.is_not_null()))
    .then(patients.date_of_death),
    otherwise = None)
)

# date of derigstration
dataset.deregistration_date = practice_registrations.for_patient_on(index_date).end_date

# define censoring date - earliest of death, deregistration or end of study period
dataset.censor_date = minimum_of(dataset.death_date, dataset.deregistration_date, end_date)

## define patient comorbidities to extract

# define medication date to find recent prescriptions
medication_date = index_date - years(1)

# create combined asthma medications codelist
asthma_meds = (
    codelists.asthma_oral_medications  # oral medications
    + codelists.asthma_inhaled_medications  # inhaled medications
)

has_asthma_diagnosis = (
    clinical_events.where(clinical_events.date.is_on_or_before(index_date))
    .where(clinical_events.snomedct_code.is_in(codelists.asthma_codelist))
    .exists_for_patient()
)

has_asthma_medication = (
    medications.where(medications.date.is_on_or_between(medication_date, index_date))
    .where(medications.dmd_code.is_in(asthma_meds))
    .exists_for_patient()
)

dataset.asthma = has_asthma_diagnosis & has_asthma_medication
