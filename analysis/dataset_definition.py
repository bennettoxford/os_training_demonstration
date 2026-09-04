# import the necessary ehrQL functionalities and tables
from ehrql import create_dataset, months, years, case, when, minimum_of
from ehrql.tables.tpp import (
    patients, 
    medications,
    clinical_events,
    ons_deaths,
    practice_registrations,
     addresses
)

# import variables which are defined in a separate file
from variable_lib import ( 
    has_a_continuous_practice_registration_spanning,
    has_prior_event,
    has_prior_meds,
    last_prior_event,
    med_years
 )
# import the codelists defined in a separate file
import codelists 

# create ehrQL generated dummy dataset
dataset = create_dataset() 

# define start of follow up period
index_date = "2020-03-01" 

# define end of follow up period
end_date = "2022-02-28"

# define the start date for required registration period
registration_date = index_date - months(3) 

# define the patients who have the required continuous registration (in this case 3 months)
registered_patients = (
    has_a_continuous_practice_registration_spanning(registration_date, index_date)
)

# define the patients who are of the correct age
age_of_interest = (
    (patients.age_on(index_date) >= 12) & (patients.age_on(index_date) <= 100)
)

# define the patients with known sex
sex_known = patients.sex.is_in(["female", "male", "intersex"]) 

# define the patients with an inhaler of interest in the two years preceding follow-up
inhaler_date = index_date - years(2)
inhaler_prescribed = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(inhaler_date, index_date))
    .exists_for_patient()
)

# define patients status: alive/dead: use ONS record if present, otherwise use GP record
death_date = ons_deaths.date.when_null_then(patients.date_of_death)
was_alive = death_date.is_after(index_date) | death_date.is_null()

# define the population of interest for study
dataset.define_population(
    registered_patients
    & age_of_interest
    & sex_known
    & inhaler_prescribed
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
    codelists.asthma_oral_medications + # oral medications
    codelists.asthma_inhaled_medications # inhaled medications
)

# identify whether patient is asthmatic
dataset.asthma = (
    # has a diagnosis code
    (has_prior_event(codelists.asthma_codelist, index_date))
    # and has been prescribed medications in year prior to index
    & (has_prior_meds(
        asthma_meds,
        index_date,
        where = medications.date.is_on_or_between(medication_date, index_date)
    ))
)

# create a combined codelist with the relevant COPD codelists
combined_copd_codes = (
    codelists.copd_codelist + # diagnosis codes
    codelists.copd_qof_codelist # review code
    )

# get the most recent COPD code
copd_date = last_prior_event(combined_copd_codes, index_date).date

# get the most recent COPD resolution code
copd_resolved_date = last_prior_event(codelists.copd_resolved_codelist, index_date).date

# identify whether patient had COPD which has been resolved
copd_unresolved = copd_resolved_date.is_null() | copd_resolved_date.is_on_or_before(copd_date)

# identify whether patient has COPD
# first checking for a COPD code and then checking for the resolution
dataset.copd = copd_date.is_not_null() & copd_unresolved

## define patient medication information to extract

# define the interval for inhalers for each year of study
med_starts, med_ends = med_years(index_date, end_date, 2)   

# number of inhaler prescriptions in year 1 of study
dataset.salbutamol_quantity_y1 = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(
        # only find medications up until censoring - if it occurs
        med_starts[1], minimum_of(med_ends[1], dataset.censor_date)
    )
    ).count_for_patient()
)

# number of inhaler prescriptions in year 2 of study
dataset.salbutamol_quantity_y2 = (case(
    # if censored in year 1, then inhaler quanitity should be null
    when(minimum_of(med_ends[1], dataset.censor_date) != med_ends[1])
    .then(None),
    otherwise = (
        medications.where(medications.dmd_code.is_in(codelists.salbutamol))
        .where(medications.date.is_on_or_between(
            # again, only find medications up until censoring - if it occurs
            med_starts[2], minimum_of(med_ends[2], dataset.censor_date)
        )
        ).count_for_patient()
    )
))
