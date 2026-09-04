# import python functions
from datetime import date
# import the dataset generation mechanism to test against
from dataset_definition import dataset 

# here we create three patients with which we can test our dataset definition
# they have various values of age, sex, ethnicity, prescription history, asthma/copd diagnosis and inhaler quantity

test_data = {

    # Expected in population with some quantity of inhalers each year
    1: {
        "practice_registrations": [
            {
                "start_date": date(2014, 2, 13),
                "end_date": date(2020, 1, 15)
            }
       ],
        "patients": [
            {
                "date_of_birth": date(1943, 2, 1),
                "sex": "female",
                "date_of_death": date(2020, 1, 12)
            }
        ],
        "addresses":[
            {
                "imd_rounded": 10000,
                "start_date": date(2014, 2, 13)
            }
        ],
        "clinical_events": [
            #Ethnicity
            {
                "date": date(2014, 2, 13),
                "snomedct_code": "733446001"
            },

            # Asthma diagnosis
            {
                "date": date(2009, 8, 12),
                "snomedct_code": "195967001",
            }
        ],
        "medications": [
            # Relevant Asthma Steroid Medication
            {
                "date": date(2016, 12, 1),
                "dmd_code": "10983311000001107"
            },

            # Inhaler prescribed in two years preceding
            {
                "date": date(2015, 8, 1),
                "dmd_code" : "3214311000001108",
            },

            # First year of inhalers
            {
                "date": date(2017, 4, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2017, 6, 6),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2017, 8, 12),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2017, 10, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2018, 2, 1),
                "dmd_code" : "3214311000001108",
            },

            # Second year of inhalers
            {
                "date": date(2018, 4, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2018, 5, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2018, 6, 6),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2018, 8, 12),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2018, 10, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2018, 12, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2019, 1, 15),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2019, 2, 21),
                "dmd_code" : "3214311000001108",
            },

            # Third year of inhalers
            {
                "date": date(2019, 4, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2019, 5, 1),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2019, 8, 12),
                "dmd_code" : "3214311000001108",
            },
            {
                "date": date(2019, 12, 1),
                "dmd_code" : "3214311000001108",
            }
        ],
        "ons_deaths": [
            {
                "date": date(2020, 1, 12)
            }
        ],
        "expected_in_population": True,
        "expected_columns": {
            "age": 74,
            "sex": "female",
            "latest_ethnicity_group": "1", # White
            "imd_quintile": "2",
            "asthma": True, # Asthma diagnosis
            "copd": False, # COPD diagnosis not present
            "salbutamol_quantity_y1": 5, # First year of inhalers
            "salbutamol_quantity_y2": 8, # Second year of inhalers
            "salbutamol_quantity_y3": 4, # Third year of inhalers
            "death_date": date(2020, 1, 12),
            "deregistration_date": date(2020, 1, 15)
        },
    },

    # Expected in population without asthma or COPD but with an inhaler in first year
    2: {
        "practice_registrations": [
            {
                "start_date": date(2016, 8, 10),
                "end_date": date(2018, 1, 1)
            }
       ],
        "patients": [
            {
                "date_of_birth": date(1977, 1, 1),
                "sex": "male"
            }
        ],
        "addresses":[
            {
                "imd_rounded": 32800,
                "start_date": date(2016, 8, 10)
            }
        ],
        "clinical_events": [
            # Ethnicity
            {
                "date": date(2016, 8, 10),
                "snomedct_code": "85371009"
            }
        ],
        "medications": [
            # Inhaler prescribed in two years preceding
            {
                "date": date(2015, 8, 1),
                "dmd_code" : "3214311000001108",
            },

            # First year of inhalers
            {
                "date": date(2017, 6, 21),
                "dmd_code" : "3214311000001108", 
            }
        ],
        "ons_deaths": [],
        "expected_in_population": True,
        "expected_columns": {
            "age": 40,
            "sex": "male",
            "imd_quintile": "5 (least deprived)",
            "latest_ethnicity_group": "4", # Black or Black British
            "asthma": False,
            "copd": False,
            "salbutamol_quantity_y1": 1, # First year of inhalers
            "salbutamol_quantity_y2": None, # Second year of inhalers - none due to censoring
            "salbutamol_quantity_y3": None, # Third year of inhalers - none due to censoring
            "death_date": None,
            "deregistration_date": date(2018, 1, 1)
        },
    },
    
    # Not expected in population
    3: {
        "practice_registrations": [
            {
                "start_date": date(2007, 12, 10),
                "end_date": None
            }
       ],
        "patients": [
            {
                "date_of_birth": date(2007, 1, 1),
                "sex": "female"
            }
        ],
        "addresses":[],
        "clinical_events": [],
        "medications": [],
        "ons_deaths": [],
        "expected_in_population": False,
    },
}
