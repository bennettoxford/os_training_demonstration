# import necessary libraries
library(here)
library(arrow)
library(tidyverse)
library(ggplot2)

## create output directories if needed
fs::dir_create(here::here("output", "sense_checks"))

# import processed dataset
df <- read_feather(
  here::here("output", "dataset_processed.arrow")
) %>% 
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
            level = "Unknown")

## frequency tables for categorical variables

# create an empty list for tables
tables <- list()

# define the categorical variables you wish to look at 
vars <- c("age_group", "sex", "ethnicity", "imd_quintile")

# loop through variables
for (var in vars) {
  
  # use table() to get frequency tables for categorical variables
  tables[[var]] <- table(df[[var]], df$year)
  
}

# turn into one table for saving
long_table <- do.call(
  rbind,
  lapply(names(tables), function(var_name) {
    tab <- as.data.frame(tables[[var_name]])
    tab$group <- var_name
    tab
  })
)

# rename and reorder columns
colnames(long_table) <- c("category", "year", "count", "group")
long_table <- long_table[, c("group", "category", "year", "count")]

# save the final table
write_csv(long_table, here::here("output", "sense_checks", "categorical_checks.csv"))

## histograms for continuous variables and dates

# create an empty list for histograms
hists <- list()

# define the continuous/date variables you wish to look at 
vars <- c("age", "salbutamol_quantity", "deregistration_date", "death_date", "censor_date")

# loop through variables
for (var in vars) {
  
  # use ggplot() to get histograms for variables of interest
  hists[[var]] <- ggplot(data = df, aes(.data[[var]])) +
    geom_histogram(stat = "bin") +
    facet_wrap(~year) + theme_bw() +
    labs(
      x = str_to_title(gsub("_", " ", var)),
      y = "Count"
    )
  
  # save the plots
  ggsave(here::here("output", "sense_checks", paste0(var, "_hist.png")))
  
}

## check missing values

# convert "Unknown" values to NA
df <- df %>% 
  mutate_if(
    is.factor,
    recode_factor,
    Unknown = NA_character_
  )

# first see how many missing values are in each column
missing <- colSums(is.na(df))
missing <- tibble(
  column = names(missing),
  no_missing = missing
)

# for columns with any missing values check what proportion are missing
df_miss <- df %>%
  select_if(~any(is.na(.))) %>%
  summarise_all(~(sum(is.na(.)/n()))) %>% 
  pivot_longer(
    cols = everything(),
    names_to = "column",
    values_to = "prop_missing"
  )

# join the two methods
df_miss_sum <- merge(missing, df_miss, by = "column")

# save the information
write_csv(df_miss_sum, here::here("output", "sense_checks", "missing_values.csv"))

## check date orders

# first define the date orders to look at
df_dates <- df %>%
  mutate(
    dereg_bf_death = if_else(deregistration_date < death_date, 1, 0, missing = 0),
    death_bf_dereg = if_else(death_date < deregistration_date, 1, 0, missing = 0),
    dereg_on_death = if_else(deregistration_date == death_date, 1, 0, missing = 0),
    censor_bf_death = if_else(censor_date < death_date, 1, 0, missing = 0),
    censor_bf_dereg = if_else(censor_date < deregistration_date, 1, 0, missing = 0),
    censor_on_dereg = if_else(censor_date == deregistration_date, 1, 0, missing = 0),
    censor_on_death = if_else(censor_date == death_date, 1, 0, missing = 0),
    censor_on_end = if_else(censor_date != deregistration_date &
                              censor_date != death_date, 1, 0, missing = 0)
  ) %>%
  # the summarise the number of those with the date ordering
  summarise(dereg_bf_death = sum(dereg_bf_death),
            death_bf_dereg = sum(death_bf_dereg),
            dereg_on_death = sum(dereg_on_death),
            censor_bf_death = sum(censor_bf_death),
            censor_bf_dereg = sum(censor_bf_dereg),
            censor_on_dereg = sum(censor_on_dereg),
            censor_on_death = sum(censor_on_death),
            censor_on_end = sum(censor_on_end),
  ) %>% 
  pivot_longer(
    cols = everything(),
    names_to = "date_order",
    values_to = "number"
  )

# save the information
write_csv(df_dates, here::here("output", "sense_checks", "date_checks.csv"))
