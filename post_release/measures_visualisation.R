# import necessary libraries
library(tidyverse)
library(here)
library(lubridate)
library(ggplot2)
library(data.table)

# create a function to visualise measures
measures_vis <- function(period) {

  # get study period dates
  source(here("analysis", "design", "design.R"))
  study_start_date <- study_dates[[paste0(period, "_start")]]
  study_end_date <- study_dates[[paste0(period, "_end")]]

  ##--- yearly measures (general population)

  #--- measures by age groups

  # import measure
  df_year_ages <- bind_rows(
    read_csv(here::here("output", paste0("measures_", period), "measure_had_prescription_by_age_yearly.csv")) %>% 
      mutate(measure = "Had Any Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_had_multiple_inhalers_by_age_yearly.csv")) %>% 
      mutate(measure = "Had Multiple Inhalers")
  )

  # plot the measures
  plot_year_ages <- df_year_ages %>%
    # add a variable indicating the year
    mutate(
      start = factor(format(interval_start, "%Y-%m")),
      age_group = str_to_title(gsub("_", " ", age_group))
    ) %>% 
    ggplot() +
    geom_bar(aes(x = age_group, y = ratio, group = start, fill = start),
            stat = "identity", position = "dodge") + facet_wrap(~measure) +
    scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
    labs(x = "Age Group", y = "Proportion of Population",
        fill = "Year Start")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_age_groups_yearly.png"),
        plot_year_ages, height = 12, width = 14)

  ##--- monthly measures (general population)

  #--- measures by age groups

  # import measure
  df_month_ages <- bind_rows(
    read_csv(here::here("output", paste0("measures_", period), "measure_had_prescription_by_age_monthly.csv")) %>% 
      mutate(measure = "Had Any Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_had_multiple_inhalers_by_age_monthly.csv")) %>% 
      mutate(measure = "Had Multiple Inhalers")
  ) %>% 
    mutate(
      start = case_when(
        interval_start >= study_start_date & interval_start < study_start_date + years(1)
        ~ paste0(year(study_start_date), "-03"),
        interval_start >= study_start_date + years(1) & interval_start < study_end_date
        ~ paste0(year(study_start_date + years(1)), "-03")
      )
    )

  # plot the measures
  plot_month_ages <- df_month_ages %>%
    # add a variable indicating the year
    mutate(
      age_group = str_to_title(gsub("_", " ", age_group))
    ) %>% 
    ggplot() +
    geom_line(aes(x = interval_start, y = ratio, colour = measure),
              linewidth = 1) + facet_wrap(~age_group) + 
    scale_colour_brewer(palette = "Accent") +
    labs(x = "Month", y = "Proportion of Population", colour = "Measure") +
    theme_bw(base_size = 18) + theme(legend.position = "top")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_age_groups_monthly.png"),
        plot_month_ages, height = 12, width = 14)

  ##--- monthly measures - concatenated into years (general population)

  #--- measures by age groups

  # collapse the numerator and denominator by year and re-calculate ratio
  df_year_ages2 <- as.data.table(df_month_ages)
  df_year_ages2 <- df_year_ages2[, .(
    numerator_year = sum(numerator),
    denominator_year = sum(denominator)
  ), by = .(start, measure, age_group)]
  df_year_ages2[, ratio_year := numerator_year / denominator_year]

  # plot the measures
  plot_year_ages2 <- df_year_ages2 %>%
    # add a variable indicating the year
    mutate(
      age_group = str_to_title(gsub("_", " ", age_group))
    ) %>% 
    ggplot() +
    geom_bar(aes(x = age_group, y = ratio_year, group = start, fill = start),
            stat = "identity", position = "dodge") + facet_wrap(~measure) +
    scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
    labs(x = "Age Group", y = "Proportion of Population",
        fill = "Year Start")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_age_groups_yearly2.png"),
        plot_year_ages2, height = 12, width = 14)

  ##---------------------

  ##--- yearly measures (restricted population)

  #--- measures by age groups

  # import measure
  df_year_ages <- bind_rows(
    read_csv(here::here("output", paste0("measures_", period), "measure_had_prescription_by_age_restricted_pop_yearly.csv")) %>% 
      mutate(measure = "Had Any Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_had_multiple_inhalers_by_age_restricted_pop_yearly.csv")) %>% 
      mutate(measure = "Had Multiple Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_has_asthma_copd_by_age_restricted_pop_yearly.csv")) %>% 
      mutate(measure = "Diagnosis of Asthma or COPD")
  )

  # plot the measures
  plot_year_ages <- df_year_ages %>%
    # add a variable indicating the year
    mutate(
      start = factor(format(interval_start, "%Y-%m")),
      age_group = str_to_title(gsub("_", " ", age_group))
    ) %>% 
    ggplot() +
    geom_bar(aes(x = age_group, y = ratio, group = start, fill = start),
            stat = "identity", position = "dodge") + facet_wrap(~measure) +
    scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
    labs(x = "Age Group", y = "Proportion of (Restricted) Population",
        fill = "Year Start")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_age_groups_restricted_pop_yearly.png"),
        plot_year_ages, height = 12, width = 14)

  #--- measures by condition

  # import measure
  df_year_conditions <- bind_rows(
    read_csv(here::here("output", paste0("measures_", period), "measure_had_prescription_by_condition_restricted_pop_yearly.csv")) %>%
      mutate(measure = "Had Any Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_had_multiple_inhalers_by_condition_restricted_pop_yearly.csv")) %>%
      mutate(measure = "Had Multiple Inhalers")
  )

  # plot the measures
  plot_year_conditions <- df_year_conditions %>%
    # add a variable indicating the year
    mutate(
      start = factor(format(interval_start, "%Y-%m")),
      condition = if_else(condition == "copd", "COPD", str_to_title(condition))
    ) %>%
    ggplot() +
    geom_bar(aes(x = condition, y = ratio, group = start, fill = start),
            stat = "identity", position = "dodge") + facet_wrap(~measure) +
    scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
    labs(x = "Respiratory Condition", y = "Proportion of Population",
        fill = "Year Start")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_conditions_restricted_pop_yearly.png"),
        plot_year_conditions, height = 12, width = 14)


  ##--- monthly measures (restricted population)

  #--- measures by age groups

  # import measure
  df_month_ages <- bind_rows(
    read_csv(here::here("output", paste0("measures_", period), "measure_had_prescription_by_age_restricted_pop_monthly.csv")) %>% 
      mutate(measure = "Had Any Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_had_multiple_inhalers_by_age_restricted_pop_monthly.csv")) %>% 
      mutate(measure = "Had Multiple Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_has_asthma_copd_by_age_restricted_pop_monthly.csv")) %>% 
      mutate(measure = "Diagnosis of Asthma or COPD")
  ) %>% 
    mutate(
      start = case_when(
        interval_start >= study_start_date & interval_start < study_start_date + years(1)
        ~ paste0(year(study_start_date), "-03"),
        interval_start >= study_start_date + years(1) & interval_start < study_end_date
        ~ paste0(year(study_start_date + years(1)), "-03")
      )
    )

  # plot the measures
  plot_month_ages <- df_month_ages %>%
    # add a variable indicating the year
    mutate(
      age_group = str_to_title(gsub("_", " ", age_group))
    ) %>% 
    ggplot() +
    geom_line(aes(x = interval_start, y = ratio, colour = measure),
              linewidth = 1) + facet_wrap(~age_group) + 
    scale_colour_brewer(palette = "Accent") +
    labs(x = "Month", y = "Proportion of Population", colour = "Measure") +
    theme_bw(base_size = 18) + theme(legend.position = "top")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_age_groups_restricted_pop_monthly.png"),
        plot_month_ages, height = 12, width = 14)

  #--- measures by condition

  # import measure
  df_month_conditions <- bind_rows(
    read_csv(here::here("output", paste0("measures_", period), "measure_had_prescription_by_condition_restricted_pop_monthly.csv")) %>%
      mutate(measure = "Had Any Inhalers"),
    read_csv(here::here("output", paste0("measures_", period), "measure_had_multiple_inhalers_by_condition_restricted_pop_monthly.csv")) %>%
      mutate(measure = "Had Multiple Inhalers")
  ) %>%
    mutate(
      start = case_when(
        interval_start >= study_start_date & interval_start < study_start_date + years(1)
        ~ paste0(year(study_start_date), "-03"),
        interval_start >= study_start_date + years(1) & interval_start < study_end_date
        ~ paste0(year(study_start_date + years(1)), "-03")
      )
    )

  # plot the measures
  plot_month_conditions <- df_month_conditions %>%
    mutate(
      condition = if_else(condition == "copd", "COPD", str_to_title(condition))
    ) %>%
    ggplot() +
    geom_line(aes(x = interval_start, y = ratio, colour = condition),
              linewidth = 1) + facet_wrap(~measure) +
    scale_colour_brewer(palette = "Dark2") +
    labs(x = "Month", y = "Proportion of Population", colour = "Condition") +
    theme_bw(base_size = 18) + theme(legend.position = "top")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_conditions_restricted_pop_monthly.png"),
        plot_month_conditions, height = 12, width = 14)

  ##--- monthly measures - concatenated into years (restricted population)

  #--- measures by age groups

  # collapse the numerator and denominator by year and re-calculate ratio
  df_year_ages2 <- as.data.table(df_month_ages)
  df_year_ages2 <- df_year_ages2[, .(
    numerator_year = sum(numerator),
    denominator_year = sum(denominator)
  ), by = .(start, measure, age_group)]
  df_year_ages2[, ratio_year := numerator_year / denominator_year]

  # plot the measures
  plot_year_ages2 <- df_year_ages2 %>%
    # add a variable indicating the year
    mutate(
      age_group = str_to_title(gsub("_", " ", age_group))
    ) %>% 
    ggplot() +
    geom_bar(aes(x = age_group, y = ratio_year, group = start, fill = start),
            stat = "identity", position = "dodge") + facet_wrap(~measure) +
    scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
    labs(x = "Age Group", y = "Proportion of Population",
        fill = "Year Start")

  # save the plot
  ggsave(here::here("output", paste0("measures_", period), "measures_by_age_groups_restricted_pop_yearly2.png"),
        plot_year_ages2, height = 12, width = 14)

  #--- measures by condition

  # collapse the numerator and denominator by year and re-calculate ratio
  df_year_conditions2 <- as.data.table(df_month_conditions)
  df_year_conditions2 <- df_year_conditions2[, .(
    numerator_year = sum(numerator),
    denominator_year = sum(denominator)
  ), by = .(start, measure, condition)]
  df_year_conditions2[, ratio_year := numerator_year / denominator_year]

  # plot the measures
  plot_year_conditions2 <- df_year_conditions2 %>%
    # add a variable indicating the year
    mutate(
      condition = if_else(condition == "copd", "COPD", str_to_title(condition))
    ) %>%
    ggplot() +
    geom_bar(aes(x = condition, y = ratio_year, group = start, fill = start),
            stat = "identity", position = "dodge") + facet_wrap(~measure) +
    scale_fill_brewer(palette = "Set2") + theme_bw(base_size = 18) +
    labs(x = "Respiratory Condition", y = "Proportion of Population",
        fill = "Year Start")

  # save the plot
  ggsave(here::here(
    "output", paste0("measures_", period), "measures_by_conditions_restricted_pop_yearly2.png"),
    plot_year_conditions2, height = 12, width = 14)

}

## pre-pandemic period
measures_vis("pre_pandemic")

## pandemic period
measures_vis("pandemic")

## post-pandemic period
measures_vis("post_pandemic")
