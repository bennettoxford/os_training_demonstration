# import the necessary ehrQL functionalities and tables
from ehrql import create_measures, years, case, when, months
from ehrql.measures import INTERVAL
from ehrql.tables.tpp import patients, medications, ons_deaths, practice_registrations

# import variables which are defined in a separate file
from variable_lib import (
    has_a_continuous_practice_registration_spanning,
    has_prior_event,
    has_prior_meds,
    last_prior_event
)
# import the codelists defined in a separate file
import codelists

# define start of follow up period
index_date = "2020-03-01" 

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

# define patients status: alive/dead: use ONS record if present, otherwise use GP record
death_date = ons_deaths.date.when_null_then(patients.date_of_death)
was_alive = death_date.is_after(index_date) | death_date.is_null()

# define the interevals to be used for the measures
intervals_years = years(2).starting_on(index_date)
intervals_months = months(24).starting_on(index_date)

# create ehrQL measures object for configuration
measures = create_measures()

# define the size of a dummy population
measures.configure_dummy_data(population_size = 250)

# restrict prescriptions to those within intervals
prescriptions_in_interval = medications.where(medications.date.is_during(INTERVAL))

# now subset these to only be those for salbutamol
relevant_prescriptions_in_interval = (
    prescriptions_in_interval.where(medications.dmd_code.is_in(codelists.salbutamol))
)

# define the patients who fit this measure
had_prescription = relevant_prescriptions_in_interval.exists_for_patient()

# define medication date to find recent prescriptions
medication_date = index_date - years(1)

# get the age of particpants
age = patients.age_on(index_date)

# classify ages
age_group = (case(
    when((age >= 12) & (age < 18)).then("adolescent"),
    when((age >= 18) & (age < 60)).then("adult"),
    when((age >= 60) & (age <= 100)).then("older_adult")
))

# define the quantity of prescriptions of salbutamol in interval
salbutamol_quantity = (
    relevant_prescriptions_in_interval.count_for_patient()
)

# define the patients who received multiple prescriptions in the interval
had_multiple = (case(
    when(salbutamol_quantity > 1).then(True),
    otherwise = False
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

# define the measure of interest: those with salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_prescription_by_age_yearly",
    numerator = had_prescription,
    group_by = {"age_group": age_group},
    intervals = intervals_years,
)

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_multiple_inhalers_by_age_yearly",
    numerator = had_multiple,
    group_by = {"age_group": age_group},
    intervals = intervals_years,
)

## monthly measures

# define the measure of interest: those with salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_prescription_by_age_monthly",
    numerator = had_prescription,
    group_by = {"age_group": age_group},
    intervals = intervals_months,
)

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_multiple_inhalers_by_age_monthly",
    numerator = had_multiple,
    group_by = {"age_group": age_group},
    intervals = intervals_months,
)

##-- create some measures for the population restricted for models

# define medication date to find recent prescriptions
medication_date = index_date - years(1)

# identify whether patient is asthmatic
asthma = (
    # has a diagnosis code
    (has_prior_event(codelists.asthma_codelist, index_date))
    # and has been prescribed medications in year prior to index
    & (
        (has_prior_meds(codelists.asthma_oral_medications, index_date, # oral medications
            where = medications.date.is_on_or_between(medication_date, index_date)))
         |(has_prior_meds(codelists.asthma_inhaled_medications, index_date, # inhaled medications
            where = medications.date.is_on_or_between(medication_date, index_date)))
    )
)

# identify whether patient had COPD which has been resolved
copd_res = (case(
    # has a resolution code
    when(last_prior_event(codelists.copd_resolved_codelist, index_date).date
    # which is dated after the latest diagnosis code
    .is_on_or_after(last_prior_event(codelists.copd_codelist, index_date).date))
    .then(True),
    # has a resolution code
    when(last_prior_event(codelists.copd_resolved_codelist, index_date).date
    # which is dated after the latest QoF code
    .is_on_or_after(last_prior_event(codelists.copd_qof_codelist, index_date).date))
    .then(True),
    otherwise = False)
)

# identify whether patient has COPD
copd = (case(
    when(
        (
            # has a copd diagnosis code
            (has_prior_event(codelists.copd_codelist, index_date)) 
            # or has a copd review code
            |(has_prior_event(codelists.copd_qof_codelist, index_date))
        )
        # and does not have COPD which has already been resolved
        & (~copd_res)
    )
    .then(True),
    otherwise = False)
)

# define whether the patient has asthma, copd, or none of the conditions of interest
has_asthma_copd = (case(
    when(asthma).then(True),
    when(copd).then(True),
    otherwise = False
))

# define whether the patient has asthma, copd, or none of the conditions of interest
condition = (case(
    when(asthma).then("asthma"),
    when(copd).then("copd"),
    otherwise = "none"
))

# define the patients with an inhaler of interest in the two years precedeing follow-up
inhaler_date = index_date - years(2)
inhaler_prescribed = (
    medications.where(medications.dmd_code.is_in(codelists.salbutamol))
    .where(medications.date.is_on_or_between(inhaler_date, index_date))
    .exists_for_patient()
)

## yearly measures

# define the measure of interest: those with salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_prescription_by_age_restricted_pop_yearly",
    numerator = had_prescription,
    denominator = denominator & inhaler_prescribed,
    group_by = {"age_group": age_group},
    intervals = intervals_years,
)

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_multiple_inhalers_by_age_restricted_pop_yearly",
    numerator = had_multiple,
    denominator = denominator & inhaler_prescribed,
    group_by = {"age_group": age_group},
    intervals = intervals_years,
)

# define the measure of interest: those with asthma or copd, by age group
measures.define_measure(
    "measure_has_asthma_copd_by_age_restricted_pop_yearly",
    numerator = has_asthma_copd,
    denominator = denominator & inhaler_prescribed,
    group_by = {"age_group": age_group},
    intervals = intervals_years,
)

# define the measure of interest: those with salbutamol inhalers prescribed, by condition
measures.define_measure(
    "measure_had_prescription_by_condition_restricted_pop_yearly",
    numerator = had_prescription,
    denominator = denominator & inhaler_prescribed,
    group_by = {"condition": condition},
    intervals = intervals_years,
)

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by condition
measures.define_measure(
    "measure_had_multiple_inhalers_by_condition_restricted_pop_yearly",
    numerator = had_multiple,
    denominator = denominator & inhaler_prescribed,
    group_by = {"condition": condition},
    intervals = intervals_years,
)

## monthly measures

# define the measure of interest: those with salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_prescription_by_age_restricted_pop_monthly",
    numerator = had_prescription,
    denominator = denominator & inhaler_prescribed,
    group_by = {"age_group": age_group},
    intervals = intervals_months,
)

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by age group
measures.define_measure(
    "measure_had_multiple_inhalers_by_age_restricted_pop_monthly",
    numerator = had_multiple,
    denominator = denominator & inhaler_prescribed,
    group_by = {"age_group": age_group},
    intervals = intervals_months,
)

# define the measure of interest: those with asthma or copd, by age group
measures.define_measure(
    "measure_has_asthma_copd_by_age_restricted_pop_monthly",
    numerator = has_asthma_copd,
    denominator = denominator & inhaler_prescribed,
    group_by = {"age_group": age_group},
    intervals = intervals_months,
)

# define the measure of interest: those with salbutamol inhalers prescribed, by condition
measures.define_measure(
    "measure_had_prescription_by_condition_restricted_pop_monthly",
    numerator = had_prescription,
    denominator = denominator & inhaler_prescribed,
    group_by = {"condition": condition},
    intervals = intervals_months,
)

# define the measure of interest: those with multiple salbutamol inhalers prescribed, by condition
measures.define_measure(
    "measure_had_multiple_inhalers_by_condition_restricted_pop_monthly",
    numerator = had_multiple,
    denominator = denominator & inhaler_prescribed,
    group_by = {"condition": condition},
    intervals = intervals_months,
)
