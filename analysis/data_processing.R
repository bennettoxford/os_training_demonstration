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

  # pivot the data to have multiple rows per patient
  df_long <- df %>% 
    pivot_longer(
      # select columns relating to salbutamol quantity
      cols = starts_with("salbutamol"),
      # create column containing the year number
      names_to = "year", 
      # removes the prefix from the column names so year = {1, 2} etc
      names_prefix = "salbutamol_quantity_y", 
      # create column of corresponding inhaler quantities for each year
      values_to = "salbutamol_quantity" 
    )

  # reorder the columns in a way that is logical for future work
  col_order <- c("patient_id", "age", "age_group", "sex", "ethnicity", "imd_quintile", 
                "asthma", "copd", "salbutamol_quantity", "year", "deregistration_date",
                "death_date", "censor", "censor_date")
  df_long <- df_long[, col_order]

  # remove rows in year two for patients censored in year 1
  df_long <- df_long %>% 
    mutate(
      # convert year to integer
      year = as.integer(year),
      # define a variable to identify those censored in year 1
      censored_in_year1 = censor_date < (study_start_date + years(1))
    ) %>%
    # drop year 2 rows when censored in year 1
    filter(!(year == 2 & censored_in_year1)) %>%     
    select(-censored_in_year1) 

  # for pre-pandemic and post-pandemic remove rows censored in second year
  if (study_start_date != as.Date("2020-03-01")) {
    df_long <- df_long %>%
      mutate(      
      # define a variable to identify those censored in year 2
      censored_in_year2 = censor_date < (study_start_date + years(2))
    ) %>%
    # drop year 3 rows when censored in year 2
    filter(!(year == 3 & censored_in_year2)) %>%     
    select(-censored_in_year2) 
  }

  # save the processed data
  write_feather(
    df_long, here::here("output", paste0(
      "dataset_processed_", period, ".arrow"))
  )

}

## pre-pandemic period
process_dataset("pre_pandemic")

## pandemic period
process_dataset("pandemic")

## post-pandemic period
process_dataset("post_pandemic")
