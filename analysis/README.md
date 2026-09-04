# Analysis folder

The 'analysis' folder is one which is created automatically when you create a project from [the OpenSAFELY research template](https://github.com/opensafely/research-template). The folder should include the `dataset_definition.py` file, in addition to any processing and analytical files. Additional file structuring with further folders may be useful for larger projects.

# What have we included?

In this folder are three ehrQL files querying the secure database:

- `dataset_definition.py` contains the query for selecting study data
- `inclusion_definition.py` contains the query for getting information for patient inclusion/exclusion numbers (e.g. for a [patient inclusion flow chart](https://www.nature.com/articles/s41586-020-2521-4/figures/1))
- `measures_definition.py` contains the query which gets information about ratios of [measures of interest](https://docs.opensafely.org/ehrql/explanation/measures/) for defined populations

There are additional files which are used for these definitions:

- `codelists.py` is a script which imports necessary codelists and instantiates them as Python objects which can then be manipulated and used in ehrQL queries; this is common convention aross OpenSAFELY projects but not a requirement
- `variable_lib.py` is a script containing variables which are used within the queries; this is a way of keeping your queries cleaner and easier to navigate. You can also use the variables across multiple query files
- `test_dataset_definition.py` is a script which uses the [OpenSAFELY assurance testing framework](https://docs.opensafely.org/ehrql/how-to/test-dataset-definition/) to test our ehrQL logic. This script defines three example patients, along with all their relevant data, and asserts whether or not each should be included in our dataset definition.

Finally, there are also files which are used downstream from the ehrQL queries and helper files:

- `inclusion_processing.R` is a script which can be used to aggregate the inclusion/exclusion information for release
- `redaction.R` is a script containing a function to be used for statistical disclosure control
- `data_processing.R` is a script which reformats the data for usage in analysis
- `table1.R` is a script which aggregates information about the study population
- `model.R` is a script in which the study analysis itself is performed
- `deciles_charts.py` is a script which can be used to create decile charts, and the underlying tables, for measures