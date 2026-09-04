# import the necessary ehrQL functionalities and tables
from ehrql import years, days
from ehrql.tables.tpp import practice_registrations, clinical_events, medications 

# define a function to return clinical events occurring before index date
def prior_events(index_date):
  return clinical_events.where(clinical_events.date.is_on_or_before(index_date))

# define a function to query prior_events(index_date) for existence of event-in-codelist. 
# This function also optionally takes an extra predicate in the 'where' variable.
def has_prior_event(codelist, index_date, where = True):
    return (
        prior_events(index_date).where(where)
        .where(prior_events(index_date).snomedct_code.is_in(codelist))
        .exists_for_patient()
    )

# define a function to return all medications prescribed before index date
def prior_meds(index_date):
  return (
      medications.where(medications.date.is_on_or_before(index_date))
)

# define a function to query prior_meds(index_date) for existence of medication-in-codelist
# This function also optionally takes an extra predicate in the 'where' variable.
def has_prior_meds(codelist, index_date, where = True):
    return (
        prior_meds(index_date).where(where)
        .where(prior_meds(index_date).dmd_code.is_in(codelist))
        .exists_for_patient()
    )
