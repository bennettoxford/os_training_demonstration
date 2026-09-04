# import necessary libraries
library(tidyverse)
library(here)
library(arrow)
library(broom)
library(broom.helpers)

# use a function to model the dataset
model_dataset <- function(period) {

  # import dataset
  df <- read_feather(
    here::here("output", paste0("dataset_processed_", period, ".arrow"))
  ) %>%
    # remove "unknown' categories for modelling
    mutate(
      across(where(is.character), ~na_if(., "unknown")),
      # turn IMD into a factor
      imd_quintile = relevel(factor(
        imd_quintile, levels = c("5 (least deprived)", "4", "3", "2", "1 (most deprived)"),
        ordered = FALSE), ref = "5 (least deprived)"
      )
    )

  # model quantity
  model <- lm(
    salbutamol_quantity ~ age + sex + ethnicity + imd_quintile + asthma + copd + year,
    data = df
  )

  # tidy the model
  model_tidy <- model %>%
    tidy_and_attach() %>% 
    tidy_add_reference_rows() %>% 
    tidy_add_estimate_to_reference_rows(conf.level = 0.95) %>% 
    tidy_add_term_labels(labels = c(age = "Age (Years)")) %>%
    tidy_remove_intercept() %>% 
    mutate(
      var_label = if_else(var_label == "copd", "COPD", str_to_title(var_label)),
      label = case_when(
        label %in% c("TRUE", "FALSE") ~ paste0(var_label, " (", str_to_title(label), ")"),
        var_label == "Year" ~ paste0("Study Year ", label),
        TRUE ~ str_to_title(label))
    )

  # save the tidied model
  write_csv(model_tidy, here::here(
    "output", paste0("model_results_", period, ".csv")))

}

## pre-pandemic period
model_dataset("pre_pandemic")

## pandemic period
model_dataset("pandemic")

## post-pandemic period
model_dataset("post_pandemic")
