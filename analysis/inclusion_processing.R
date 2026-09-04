library(here)
library(tidyverse)
library(readr)
library(arrow)

# import function for statistical disclosure control
source(here::here("analysis", "redaction.R"))

# import the dataset
patients_df <- read_feather(here::here("output", "population.arrow"))

# define the base population for exclusion: only consider alive and appropriate age patients
population <- patients_df %>%
    mutate(
        stage0 = 1,
        stage1 = registered, # patients with three months prior registration
        stage2a = registered & sex_known, # registered patients with enough data quality (sex)
        stage2b = registered & inhaler_prescribed, # registered patients with prior inhalers
        stage2 = registered & sex_known & inhaler_prescribed # included patients
    )

# apply disclosure control and then get percentages 
population_summary <- population %>%
    summarise(
        n0 = roundmid_any(n()),
        n1 = roundmid_any(sum(stage1, na.rm = TRUE)),
        n2a = roundmid_any(sum(stage2a, na.rm = TRUE)),
        n2b = roundmid_any(sum(stage2b, na.rm = TRUE)),
        n2 = roundmid_any(sum(stage2, na.rm = TRUE)),
        
        pct1 = n1 / n0 * 100,
        pct2a = n2a / n1 * 100,
        pct2b = n2b / n1 * 100,
        pct2 = n2 / n1 * 100
    )

# save the aggregated summary
write_csv(population_summary, path = here::here(
    "output", "population_processed.csv"))
