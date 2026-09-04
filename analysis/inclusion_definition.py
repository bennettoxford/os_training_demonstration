# import the necessary ehrQL functionalities and tables
from ehrql import create_dataset, months, years
from ehrql.tables.core import patients, medications, ons_deaths

# import variables which are defined in a separate file
from variable_lib import has_a_continuous_practice_registration_spanning
import codelists

# create ehrQL dataset object for adding a population definition and data columns
dataset = create_dataset() 

# define start of follow up period
index_date = "2020-03-01" 

# define end of follow up period
end_date = "2022-02-28"

# define patients status: alive/dead: use ONS record if present, otherwise use GP record
death_date = ons_deaths.date.when_null_then(patients.date_of_death)
was_alive = death_date.is_after(index_date) | death_date.is_null()

# define the patients who are of the correct age
age_of_interest = (
    (patients.age_on(index_date) >= 12) & (patients.age_on(index_date) <= 100)
)

# define the population for eligible for study - age of interest who is alive
dataset.define_population(
    was_alive &
    age_of_interest
)

# define the start date for required registration period
registration_date = index_date - months(3) 

# define the patients who have the required continuous registration (in this case 3 months)
registered_patients = (
    has_a_continuous_practice_registration_spanning(registration_date, index_date)
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

# add the variable for inclusion/exclusion information to a dataset
dataset.registered = registered_patients
dataset.sex_known = sex_known
dataset.inhaler_prescribed = inhaler_prescribed
