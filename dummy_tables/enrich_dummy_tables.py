# import necessary python libraries
import pandas as pd
import numpy as np

###-- Pre-Pandemic

##--- Clinical Events

# import the data you want to enrich
events = pd.read_csv(
    'dummy_tables/dummy_tables_pre_pandemic/clinical_events.csv',
    dtype={'snomedct_code': 'string'}
)

## first we need to change the *codes*

# get a sample of patients to give the codes to 
events_sample = (
    #first get one row per patient and then get 70% of patients
    events.groupby("patient_id").sample(n = 1).sample(frac = 0.7)
)

# get the codes you want to use
asthma_codes = (
    pd.read_csv('codelists/nhsd-primary-care-domain-refsets-ast_cod.csv',
    dtype = {'code': 'string'})  
)

# assign every patient in the sample a random relevant code
events_sample['snomedct_code'] = pd.Series(
    np.random.choice(
        asthma_codes['code'].dropna().to_numpy(),
        size=len(events_sample),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample], ignore_index = True)

## need to also add codes for ethnicity

# get a sample of patients to give the codes to 
events_sample_ethnicity = (
    #get one row per patient
    events.groupby("patient_id").sample(n = 1)
)

# get the codes to use
ethnicity_codes = (
    pd.read_csv('codelists/opensafely-ethnicity-snomed-0removed.csv',
    dtype = {'code': 'string'})   
)

# assign every patient a random relevant code
events_sample_ethnicity['snomedct_code'] = pd.Series(
    np.random.choice(
        ethnicity_codes['code'].dropna().to_numpy(),
        size=len(events_sample_ethnicity),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample_ethnicity], ignore_index = True)

# save the changes made 
events.to_csv('dummy_tables/dummy_tables_pre_pandemic/clinical_events.csv', index = False)

##--- Medications

# import the data you want to enrich
meds = pd.read_csv('dummy_tables/dummy_tables_pre_pandemic/medications.csv')

## first we need to change the *codes*

# import codelist which you want codes from
inhaler_codes = pd.read_csv('codelists/nhs-drug-refsets-gensalbdpinhdrug_cod.csv')

# transform the codes to ones that match the desired codelist - these are selected randomly
meds['dmd_code'] = np.random.choice(
    inhaler_codes['code'], 
    size = len(meds), 
    replace = True
)

## then we need to change the *dates*

# define the date range for the codes of interest
start = np.datetime64("2015-03-01")
end   = np.datetime64("2020-02-29")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds))

# now assign dates within the range needed
meds['date'] = start + random_days

## now we can repeat the rows we want - in this case, all the inhalers after indexing (we need some before indexing as the same table is used to identify patients)

# define the date range of interest
repeat_start = np.datetime64("2017-03-01")
repeat_end   = np.datetime64("2020-02-29")

# filter the eligible rows
eligible = meds[(meds['date'] >= repeat_start) & (meds['date'] <= repeat_end)]

# repeat the eligible rows 10 times
eligible_repeated = pd.concat([eligible] * 10, ignore_index = True)

# combine with original data
meds_expanded = pd.concat([meds, eligible_repeated], ignore_index = True)

## we now need to add medication codes for another medication type, to meet a separate definition

# for patients with the relevant clinical event, we need them to also have a medication code
patients_with_event = events_sample['patient_id'].unique()

# get the rows in the table for the correct patients
meds_rows_patients = meds.loc[meds['patient_id'].isin(patients_with_event) == True].copy()

# get codelist with relevant medication codes
oral_med_codes = pd.read_csv('codelists/nhs-drug-refsets-c19astdrug_cod.csv')

# assign relevant medication codes to these patients
meds_rows_patients['dmd_code'] = np.random.choice(
    oral_med_codes['code'], 
    size = len(meds_rows_patients), 
    replace = True
)

# define the date range for the codes of interest
start = np.datetime64("2016-03-01")
end   = np.datetime64("2017-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds_rows_patients))

# now assign dates within the range needed
meds_rows_patients['date'] = start + random_days

# combine this with the rest of the dummy medications data
meds_expanded = pd.concat([meds_expanded, meds_rows_patients], ignore_index = True)

# save the changes made 
meds_expanded.to_csv('dummy_tables/dummy_tables_pre_pandemic/medications.csv', index = False)

##--- Practice Registrations

## add practice deregistrations for some individuals

# first get current registrations table
registrations = pd.read_csv(
    'dummy_tables/dummy_tables_pre_pandemic/practice_registrations.csv',
    dtype={'snomedct_code': 'string'}
)

# define the date range for the codes of interest
start_reg = np.datetime64("2017-03-01")
end_reg   = np.datetime64("2020-02-29")

# get the number of days between start and end
days = (end_reg - start_reg).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = 50)

# choose how many rows to update (max 50, but never more than len)
n = min(50, len(registrations))

# randomly pick row indices
random_idx = np.random.choice(registrations.index, size = n, replace = False)

# initialize column with correct dtype
registrations['end_date'] = pd.Series(pd.NaT, dtype = 'datetime64[ns]')

# assign the end dates at random locations
registrations.loc[random_idx, 'end_date'] = start_reg + random_days

# save the changes made 
registrations.to_csv('dummy_tables/dummy_tables_pre_pandemic/practice_registrations.csv', index = False)

###-- Pandemic

##--- Clinical Events

# import the data you want to enrich
events = pd.read_csv(
    'dummy_tables/dummy_tables_pandemic/clinical_events.csv',
    dtype={'snomedct_code': 'string'}
)

## first we need to change the *codes*

# get a sample of patients to give the codes to 
events_sample = (
    #first get one row per patient and then get 70% of patients
    events.groupby("patient_id").sample(n = 1).sample(frac = 0.7)
)

# get the codes you want to use
asthma_codes = (
    pd.read_csv('codelists/nhsd-primary-care-domain-refsets-ast_cod.csv',
    dtype = {'code': 'string'})  
)

# assign every patient in the sample a random relevant code
events_sample['snomedct_code'] = pd.Series(
    np.random.choice(
        asthma_codes['code'].dropna().to_numpy(),
        size=len(events_sample),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample], ignore_index = True)

## need to also add codes for ethnicity

# get a sample of patients to give the codes to 
events_sample_ethnicity = (
    #get one row per patient
    events.groupby("patient_id").sample(n = 1)
)

# get the codes to use
ethnicity_codes = (
    pd.read_csv('codelists/opensafely-ethnicity-snomed-0removed.csv',
    dtype = {'code': 'string'})   
)

# assign every patient a random relevant code
events_sample_ethnicity['snomedct_code'] = pd.Series(
    np.random.choice(
        ethnicity_codes['code'].dropna().to_numpy(),
        size=len(events_sample_ethnicity),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample_ethnicity], ignore_index = True)

# save the changes made 
events.to_csv('dummy_tables/dummy_tables_pandemic/clinical_events.csv', index = False)

##--- Medications

# import the data you want to enrich
meds = pd.read_csv('dummy_tables/dummy_tables_pandemic/medications.csv')

## first we need to change the *codes*

# import codelist which you want codes from
inhaler_codes = pd.read_csv('codelists/nhs-drug-refsets-gensalbdpinhdrug_cod.csv')

# transform the codes to ones that match the desired codelist - these are selected randomly
meds['dmd_code'] = np.random.choice(
    inhaler_codes['code'], 
    size = len(meds), 
    replace = True
)

## then we need to change the *dates*

# define the date range for the codes of interest
start = np.datetime64("2018-03-01")
end   = np.datetime64("2022-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds))

# now assign dates within the range needed
meds['date'] = start + random_days

## now we can repeat the rows we want - in this case, all the inhalers after indexing (we need some before indexing as the same table is used to identify patients)

# define the date range of interest
repeat_start = np.datetime64("2020-03-01")
repeat_end   = np.datetime64("2022-02-28")

# filter the eligible rows
eligible = meds[(meds['date'] >= repeat_start) & (meds['date'] <= repeat_end)]

# repeat the eligible rows 10 times
eligible_repeated = pd.concat([eligible] * 10, ignore_index = True)

# combine with original data
meds_expanded = pd.concat([meds, eligible_repeated], ignore_index = True)

## we now need to add medication codes for another medication type, to meet a separate definition

# for patients with the relevant clinical event, we need them to also have a medication code
patients_with_event = events_sample['patient_id'].unique()

# get the rows in the table for the correct patients
meds_rows_patients = meds.loc[meds['patient_id'].isin(patients_with_event) == True].copy()

# get codelist with relevant medication codes
oral_med_codes = pd.read_csv('codelists/nhs-drug-refsets-c19astdrug_cod.csv')

# assign relevant medication codes to these patients
meds_rows_patients['dmd_code'] = np.random.choice(
    oral_med_codes['code'], 
    size = len(meds_rows_patients), 
    replace = True
)

# define the date range for the codes of interest
start = np.datetime64("2019-03-01")
end   = np.datetime64("2020-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds_rows_patients))

# now assign dates within the range needed
meds_rows_patients['date'] = start + random_days

# combine this with the rest of the dummy medications data
meds_expanded = pd.concat([meds_expanded, meds_rows_patients], ignore_index = True)

# save the changes made 
meds_expanded.to_csv('dummy_tables/dummy_tables_pandemic/medications.csv', index = False)

##--- Practice Registrations

## add practice deregistrations for some individuals

# first get current registrations table
registrations = pd.read_csv(
    'dummy_tables/dummy_tables_pandemic/practice_registrations.csv',
    dtype={'snomedct_code': 'string'}
)

# define the date range for the codes of interest
start_reg = np.datetime64("2020-03-01")
end_reg   = np.datetime64("2022-02-28")

# get the number of days between start and end
days = (end_reg - start_reg).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = 50)

# choose how many rows to update (max 50, but never more than len)
n = min(50, len(registrations))

# randomly pick row indices
random_idx = np.random.choice(registrations.index, size = n, replace = False)

# initialize column with correct dtype
registrations['end_date'] = pd.Series(pd.NaT, dtype = 'datetime64[ns]')

# assign the end dates at random locations
registrations.loc[random_idx, 'end_date'] = start_reg + random_days

# save the changes made 
registrations.to_csv('dummy_tables/dummy_tables_pandemic/practice_registrations.csv', index = False)

###-- Post-Pandemic

##--- Clinical Events

# import the data you want to enrich
events = pd.read_csv(
    'dummy_tables/dummy_tables_post_pandemic/clinical_events.csv',
    dtype={'snomedct_code': 'string'}
)

## first we need to change the *codes*

# get a sample of patients to give the codes to 
events_sample = (
    #first get one row per patient and then get 70% of patients
    events.groupby("patient_id").sample(n = 1).sample(frac = 0.7)
)

# get the codes you want to use
asthma_codes = (
    pd.read_csv('codelists/nhsd-primary-care-domain-refsets-ast_cod.csv',
    dtype = {'code': 'string'})  
)

# assign every patient in the sample a random relevant code
events_sample['snomedct_code'] = pd.Series(
    np.random.choice(
        asthma_codes['code'].dropna().to_numpy(),
        size=len(events_sample),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample], ignore_index = True)

## need to also add codes for ethnicity

# get a sample of patients to give the codes to 
events_sample_ethnicity = (
    #get one row per patient
    events.groupby("patient_id").sample(n = 1)
)

# get the codes to use
ethnicity_codes = (
    pd.read_csv('codelists/opensafely-ethnicity-snomed-0removed.csv',
    dtype = {'code': 'string'})   
)

# assign every patient a random relevant code
events_sample_ethnicity['snomedct_code'] = pd.Series(
    np.random.choice(
        ethnicity_codes['code'].dropna().to_numpy(),
        size=len(events_sample_ethnicity),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample_ethnicity], ignore_index = True)

# save the changes made 
events.to_csv('dummy_tables/dummy_tables_pandemic/clinical_events.csv', index = False)

##--- Medications

# import the data you want to enrich
meds = pd.read_csv('dummy_tables/dummy_tables_pandemic/medications.csv')

## first we need to change the *codes*

# import codelist which you want codes from
inhaler_codes = pd.read_csv('codelists/nhs-drug-refsets-gensalbdpinhdrug_cod.csv')

# transform the codes to ones that match the desired codelist - these are selected randomly
meds['dmd_code'] = np.random.choice(
    inhaler_codes['code'], 
    size = len(meds), 
    replace = True
)

## then we need to change the *dates*

# define the date range for the codes of interest
start = np.datetime64("2020-03-01")
end   = np.datetime64("2025-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds))

# now assign dates within the range needed
meds['date'] = start + random_days

## now we can repeat the rows we want - in this case, all the inhalers after indexing (we need some before indexing as the same table is used to identify patients)

# define the date range of interest
repeat_start = np.datetime64("2022-03-01")
repeat_end   = np.datetime64("2025-02-28")

# filter the eligible rows
eligible = meds[(meds['date'] >= repeat_start) & (meds['date'] <= repeat_end)]

# repeat the eligible rows 10 times
eligible_repeated = pd.concat([eligible] * 10, ignore_index = True)

# combine with original data
meds_expanded = pd.concat([meds, eligible_repeated], ignore_index = True)

## we now need to add medication codes for another medication type, to meet a separate definition

# for patients with the relevant clinical event, we need them to also have a medication code
patients_with_event = events_sample['patient_id'].unique()

# get the rows in the table for the correct patients
meds_rows_patients = meds.loc[meds['patient_id'].isin(patients_with_event) == True].copy()

# get codelist with relevant medication codes
oral_med_codes = pd.read_csv('codelists/nhs-drug-refsets-c19astdrug_cod.csv')

# assign relevant medication codes to these patients
meds_rows_patients['dmd_code'] = np.random.choice(
    oral_med_codes['code'], 
    size = len(meds_rows_patients), 
    replace = True
)

# define the date range for the codes of interest
start = np.datetime64("2021-03-01")
end   = np.datetime64("2025-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds_rows_patients))

# now assign dates within the range needed
meds_rows_patients['date'] = start + random_days

# combine this with the rest of the dummy medications data
meds_expanded = pd.concat([meds_expanded, meds_rows_patients], ignore_index = True)

# save the changes made 
meds_expanded.to_csv('dummy_tables/dummy_tables_post_pandemic/medications.csv', index = False)

##--- Practice Registrations

## add practice deregistrations for some individuals

# first get current registrations table
registrations = pd.read_csv(
    'dummy_tables/dummy_tables_post_pandemic/practice_registrations.csv',
    dtype={'snomedct_code': 'string'}
)

# define the date range for the codes of interest
start_reg = np.datetime64("2022-03-01")
end_reg   = np.datetime64("2025-02-28")

# get the number of days between start and end
days = (end_reg - start_reg).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = 50)

# choose how many rows to update (max 50, but never more than len)
n = min(50, len(registrations))

# randomly pick row indices
random_idx = np.random.choice(registrations.index, size = n, replace = False)

# initialize column with correct dtype
registrations['end_date'] = pd.Series(pd.NaT, dtype = 'datetime64[ns]')

# assign the end dates at random locations
registrations.loc[random_idx, 'end_date'] = start_reg + random_days

# save the changes made 
registrations.to_csv('dummy_tables/dummy_tables_post_pandemic/practice_registrations.csv', index = False)

###-- Post-Pandemic

##--- Clinical Events

# import the data you want to enrich
events = pd.read_csv(
    'dummy_tables/dummy_tables_post_pandemic/clinical_events.csv',
    dtype={'snomedct_code': 'string'}
)

## first we need to change the *codes*

# get a sample of patients to give the codes to 
events_sample = (
    #first get one row per patient and then get 70% of patients
    events.groupby("patient_id").sample(n = 1).sample(frac = 0.7)
)

# get the codes you want to use
asthma_codes = (
    pd.read_csv('codelists/nhsd-primary-care-domain-refsets-ast_cod.csv',
    dtype = {'code': 'string'})  
)

# assign every patient in the sample a random relevant code
events_sample['snomedct_code'] = pd.Series(
    np.random.choice(
        asthma_codes['code'].dropna().to_numpy(),
        size=len(events_sample),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample], ignore_index = True)

## need to also add codes for ethnicity

# get a sample of patients to give the codes to 
events_sample_ethnicity = (
    #get one row per patient
    events.groupby("patient_id").sample(n = 1)
)

# get the codes to use
ethnicity_codes = (
    pd.read_csv('codelists/opensafely-ethnicity-snomed-0removed.csv',
    dtype = {'code': 'string'})   
)

# assign every patient a random relevant code
events_sample_ethnicity['snomedct_code'] = pd.Series(
    np.random.choice(
        ethnicity_codes['code'].dropna().to_numpy(),
        size=len(events_sample_ethnicity),
        replace=True
    ),
    dtype="string"
)

# add these modified rows back into the dummy table
events = pd.concat([events, events_sample_ethnicity], ignore_index = True)

# save the changes made 
events.to_csv('dummy_tables/dummy_tables_pandemic/clinical_events.csv', index = False)

##--- Medications

# import the data you want to enrich
meds = pd.read_csv('dummy_tables/dummy_tables_pandemic/medications.csv')

## first we need to change the *codes*

# import codelist which you want codes from
inhaler_codes = pd.read_csv('codelists/nhs-drug-refsets-gensalbdpinhdrug_cod.csv')

# transform the codes to ones that match the desired codelist - these are selected randomly
meds['dmd_code'] = np.random.choice(
    inhaler_codes['code'], 
    size = len(meds), 
    replace = True
)

## then we need to change the *dates*

# define the date range for the codes of interest
start = np.datetime64("2020-03-01")
end   = np.datetime64("2025-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds))

# now assign dates within the range needed
meds['date'] = start + random_days

## now we can repeat the rows we want - in this case, all the inhalers after indexing (we need some before indexing as the same table is used to identify patients)

# define the date range of interest
repeat_start = np.datetime64("2022-03-01")
repeat_end   = np.datetime64("2025-02-28")

# filter the eligible rows
eligible = meds[(meds['date'] >= repeat_start) & (meds['date'] <= repeat_end)]

# repeat the eligible rows 10 times
eligible_repeated = pd.concat([eligible] * 10, ignore_index = True)

# combine with original data
meds_expanded = pd.concat([meds, eligible_repeated], ignore_index = True)

## we now need to add medication codes for another medication type, to meet a separate definition

# for patients with the relevant clinical event, we need them to also have a medication code
patients_with_event = events_sample['patient_id'].unique()

# get the rows in the table for the correct patients
meds_rows_patients = meds.loc[meds['patient_id'].isin(patients_with_event) == True].copy()

# get codelist with relevant medication codes
oral_med_codes = pd.read_csv('codelists/nhs-drug-refsets-c19astdrug_cod.csv')

# assign relevant medication codes to these patients
meds_rows_patients['dmd_code'] = np.random.choice(
    oral_med_codes['code'], 
    size = len(meds_rows_patients), 
    replace = True
)

# define the date range for the codes of interest
start = np.datetime64("2021-03-01")
end   = np.datetime64("2025-02-28")

# get the number of days between start and end
days = (end - start).astype(int)

# pick a random number of days to add to the start - for each row in the csv
random_days = np.random.randint(0, days + 1, size = len(meds_rows_patients))

# now assign dates within the range needed
meds_rows_patients['date'] = start + random_days

# combine this with the rest of the dummy medications data
meds_expanded = pd.concat([meds_expanded, meds_rows_patients], ignore_index = True)

# save the changes made 
meds_expanded.to_csv('dummy_tables/dummy_tables_post_pandemic/medications.csv', index = False)
