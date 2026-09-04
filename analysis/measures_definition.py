# import the necessary ehrQL functionalities and tables
from ehrql import create_measures, years, case, when, months
from ehrql.measures import INTERVAL
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    medications,
    ons_deaths,
    practice_registrations
)

# import the codelists defined in a separate file
import codelists

# import functions from variable library
from variable_lib import has_prior_event, has_prior_meds

# define start of follow up period
index_date = "2020-03-01" 

# define the patients who have are registered on index date
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
intervals_years = years(2).starting_on(index_date)
intervals_months = months(24).starting_on(index_date)

# create ehrQL measures object for configuration
measures = create_measures()

# define the size of a dummy population
measures.configure_dummy_data(population_size = 250)
