# import ehrql function for importing codelists
from ehrql import codelist_from_csv

# asthma diagnosis
asthma_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ast_cod.csv",
    column = "code"
)
# asthma medications (oral)
asthma_oral_medications = codelist_from_csv(
    "codelists/nhs-drug-refsets-c19astdrug_cod.csv",
    column = "code"
)
# asthma medications (inhaled)
asthma_inhaled_medications = codelist_from_csv(
    "codelists/nhs-drug-refsets-asttrtatrisk1_cod.csv",
    column = "code"
)