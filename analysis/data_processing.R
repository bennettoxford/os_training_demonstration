# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(lubridate)

# use a function to process the dataset
process_dataset <- function(period) {

  # import dataset
  df <- read_feather(
      here::here("output", paste0("dataset_", period, ".arrow"))
  )

  # get study period dates
  source(here("analysis", "design", "design.R"))
  study_start_date <- study_dates[[paste0(period, "_start")]]
  study_end_date <- study_dates[[paste0(period, "_end")]]

  # reformat some of the data
  df <- df %>%
    mutate(
      # add labels to ethnicity
      ethnicity = relevel(factor(
        latest_ethnicity_group, levels = c("1", "2", "3", "4", "5"),
        labels = c("White", "Mixed", "Asian or Asian British",
                  "Black or Black British", "Other Ethnic Groups"),
        ordered = FALSE),
        ref = "White"
      ),
      # turn IMD into a factor
      imd_quintile = relevel(factor(
        imd_quintile, ordered = FALSE),
        ref = "5 (least deprived)"
      ),
      # turn sex into a factor for models
      sex = relevel(factor(
        str_to_title(sex),
        levels = c("Female", "Male", "Intersex")),
        ref = "Female"
      ),
      # add grouping variable for age
      age_group = relevel(factor(
        case_when(age >= 12 & age < 18 ~ "Adolescent",
                  age >= 18 & age < 60 ~ "Adult",
                  age >= 60 & age <= 110 ~ "Older Adult"),
        levels = c("Adolescent", "Adult", "Older Adult"),
        ordered = FALSE),
        ref = "Adult"
      ),
      # create censor date
      censor_date = pmin(
        death_date, deregistration_date, study_end_date, na.rm = TRUE
      ),
      # create censoring variable
      censor = if_else(
        censor_date < study_end_date, 1, 0
      )
  ) %>% select(-latest_ethnicity_group)

  # reorder the columns in a way that is logical for future work
  col_order <- c("patient_id", "age", "age_group", "sex", "ethnicity", "imd_quintile", 
                "asthma", "deregistration_date", "death_date", "censor", "censor_date")
  df <- df[, col_order]

  # save the processed data
  write_feather(df, here::here("output", paste0("dataset_processed_", period, ".arrow")))

}

## pre-pandemic period
process_dataset("pre_pandemic")

## pandemic period
process_dataset("pandemic")

## post-pandemic period
process_dataset("post_pandemic")