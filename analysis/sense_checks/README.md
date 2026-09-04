# Sense checking code

Within this folder is a series of scripts designed to check the restults of data extraction/processing to look for any outliers, nuanced patterns within the data and the appropriateness of definitions. 

## The checks

There are is an R script which contains the code for the following:

- Frequency tables for categorical variables;
- Histograms for continuous variables and dates;
- Proportions of missing values in variables with missingness;
- Comparisons of date orders for date of death / deregistration / censoring

Results of the checks are saved in the `output/sense_checks` folder.