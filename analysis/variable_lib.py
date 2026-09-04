# import the necessary ehrQL functionalities and tables
from ehrql import years, days
from ehrql.tables.tpp import practice_registrations, clinical_events, medications 

# create a function to extract registrations which fully cover a given period
def _registrations_overlapping_period(start_date, end_date):
    # rename registrations table to simplify notation
    regs = practice_registrations
    #return the registrations table where registrations are continuous for a defined period 
    return regs.where(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )

# create a function to determine whether a patient has a continous registration for a defined interval
def has_a_continuous_practice_registration_spanning(start_date, end_date):
    return _registrations_overlapping_period(start_date, end_date).exists_for_patient()

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

# define a function to query prior_events(index_date) for date of most recent event-in-codelist
def last_prior_event(codelist, index_date, where = True):
    return (
        prior_events(index_date).where(where)
        .where(prior_events(index_date).snomedct_code.is_in(codelist))
        .sort_by(clinical_events.date)
        .last_for_patient()
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

# define a function to set medication periods for analysis
# - dependent on number of years in study
def med_years(index_date, end_date, year_number) :
    # create empty lists for dates
    start_dates = []
    end_dates = []
    # define the relevant dates
    for n in range(year_number + 1):
        # set the start of study plus the number of years already accounted for (n - 1 years) 
        start = index_date + years(n - 1)
        if n == year_number :
            # ensure for final year of study the end date matches precisely
            end = end_date 
        else :
            # end of interval is one year after start, subtract one day so that there is no start/end overlap
            end = start + years(1) - days(1) 
        # add the dates calculated to the relevant list
        start_dates.append(start)
        end_dates.append(end)
    # return the two lists
    return(start_dates, end_dates)
