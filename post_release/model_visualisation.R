library(tidyverse)
library(ggplot2)

# import the model results
model_tidy <- read_csv(here::here("output", "model_results.csv"))

# define the order for the variables
var_order <- c("Female", "Male", "Intersex", "Age (Years)",
               "White", "Mixed", "Asian Or Asian British",
               "Black Or Black British", "Other Ethnic Groups",
               "5 (Least Deprived)", "4", "3", "2", "1 (Most Deprived)", 
               "Asthma (False)", "Asthma (True)", "COPD (False)",
               "COPD (True)", "Study Year 1", "Study Year 2")

# create forest plot
plot <- model_tidy %>% 
  ggplot(aes(y = factor(label, levels = rev(var_order)), x = estimate,
             xmin = conf.low, xmax = conf.high)) +
  geom_vline(xintercept = 0, linetype = 2) +
  labs(y = "Parameter", x = "Estimate") +
  geom_pointrange(position = position_dodge(width = 0.75), size = 0.5) +
  theme_bw()

# add shading
dat_ribbon <- plot$data %>%
  select(variable, label, var_nlevels) %>%
  unique() %>%
  mutate(
    xmin = min(plot$data$conf.low, na.rm = T),
    xmax = max(plot$data$conf.high, na.rm = T),
    label = factor(label, levels = rev(var_order))
  ) %>%
  arrange(label) %>%
  mutate(
    yposition = seq_len(n()),
    ymin = yposition - 0.5,
    ymax = yposition + 0.5
  ) %>%
  # assign a group order based on where each variable first appears in the arranged data
  mutate(group_id = match(variable, unique(variable))) %>%
  mutate(fill = if_else(group_id %% 2 == 1, "a", "b"))

dat_ribbon_long <- dat_ribbon %>%
  pivot_longer(cols = c(xmin, xmax), values_to = "x",
               names_to = "xmin_xmax") %>%
  select(-xmin_xmax)

plot <- plot +
  geom_ribbon(
    data = dat_ribbon_long,
    aes(x = x, ymin = ymin, ymax = ymax, group = yposition, fill = fill),
    inherit.aes = FALSE,
    alpha = 0.2
  ) +
  scale_fill_manual(
    values = c("a" = "transparent", "b" = "grey50"),
    guide = "none"
  )
plot
