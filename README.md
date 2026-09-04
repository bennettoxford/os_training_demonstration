# Outline for running this as a live session

## Dataset definition

Work through a stripped back version of the dataset definition and add back chunks at a time
  - [dummy data](https://github.com/opensafely/demo_repo/tree/main/dummy_tables): talk about the different methods of dummy data generation

Add back in ethnicity

  - add ethnicity codelist using `codelists add`
  
    `opensafely codelists add https://www.opencodelists.org/codelist/opensafely/ethnicity-snomed-0removed/22911876/`

  - add ethnicity codelist to `codelists.py`

```
# ethnicity codes; see category columns here: https://www.opencodelists.org/codelist/opensafely/ethnicity-snomed-0removed/22911876/
ethnicity_codes = codelist_from_csv(
  "codelists/opensafely-ethnicity-snomed-0removed.csv",
  column = "code",
  category_column = "Grouping_6",
)
```

  - add ethnicity variable to dataset definition

```
# patient ethnicity (5 groups from 2001 census)
dataset.latest_ethnicity_group = (
    clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity_codes))
    .where(clinical_events.date.is_on_or_before(index_date))
    .sort_by(clinical_events.date)
    .last_for_patient().snomedct_code
    .to_category(codelists.ethnicity_codes)
)
```

Then add censoring chunk

```
# date of death
dataset.death_date = (case(
    when(ons_deaths.date.is_not_null())
    .then(ons_deaths.date),
    when((ons_deaths.date.is_null()) & (patients.date_of_death.is_not_null()))
    .then(patients.date_of_death),
    otherwise = None)
)

# date of deregistration
dataset.deregistration_date = practice_registrations.for_patient_on(index_date).end_date

# define censoring date - earliest of death, deregistration or end of study period
dataset.censor_date = minimum_of(dataset.death_date, dataset.deregistration_date, end_date)
```

Finally add asthma in

```
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
```

Mention ability to create functions (in variable lib) - these will then be used in the measures definition

## Measures definition
  
Walk through measures definition, starting with a cut back version and first add in the set up

```
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
```

Then create two simple measures

```
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
```

## Pipeline Overview

Highlight the main steps using the project.yaml:

- generate_dataset
- process_dataset
   - simple processing of variables to prepare for analysis
- check_dataset
   - sense checks of aggregate variable values
- summarise_dataset
   - example of creating a Table 1 for a paper
- analyse_dataset
   - simple regression analysis
- generate_measures

## Final Step: run `opensafely run run_all` in terminal
