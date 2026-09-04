# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(gtsummary)
library(readr)

# import dataset
df <- read_feather(
  here::here("output", "dataset_processed.arrow")
)

# summarise the patient characteristics
gt_table <- df %>% 
  select(-c(patient_id, censor, deregistration_date, death_date, censor_date)) %>% 
  mutate(
    # turn IMD into an ordered factor
    imd_quintile = factor(
      str_to_title(imd_quintile),
      levels = c("5 (Least Deprived)", "4", "3", "2", "1 (Most Deprived)", "Unknown"),
      ordered = TRUE),
    # turn age group into an ordered factor
    age_group = factor(
      age_group,
      levels = c("Older Adult", "Adult", "Adolescent"),
      ordered = TRUE)
    ) %>%
  # change NA values to "Unknown"
  mutate_if(is.factor,
            forcats::fct_na_value_to_level,
            level = "Unknown") %>% 
  # order IMD and age group for table
  arrange(imd_quintile, age_group) %>% 
  # create a summary table by year
  tbl_summary(
    by = year,
    label = list(age = "Patient Age",
                 age_group = "Age Group",
                 sex = "Sex",
                 ethnicity = "Ethnicity",
                 imd_quintile = "IMD Quintile",
                 asthma = "Asthma Diagnosis",
                 copd = "COPD Diagnosis",
                 salbutamol_quantity = "Salbutamol Quantity"),
    # get average salbulatmol quantity per year for population
    statistic = list(salbutamol_quantity ~ "{mean} ({sd})")
    )  %>% 
  # add the study years into header
  modify_header(list(
      stat_1 ~ "**2020-21**, N = {n}",
      stat_2 ~ "**2021-22**, N = {n}"
    )) %>% 
  # convert to format which can be saved as csv
  as_tibble()

# save the file
write_csv(gt_table, path = here::here("output", "table1.csv"))
