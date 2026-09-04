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

# copd resolution
copd_resolved_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copdres_cod.csv",
    column = "code"
)

# copd diagnosis
copd_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copd_cod.csv",
    column = "code"
)

# copd medications
copd_medications = codelist_from_csv(
    "codelists/nhs-drug-refsets-c19copddrug_cod.csv",
    column = "code"
)

# copd review
copd_qof_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copdrvw_cod.csv",
    column = "code"
)

# Generic salbutamol MDI inhalers
salbutamol_mdi = codelist_from_csv(
    "codelists/nhs-drug-refsets-gensalbmdiinhdrug_cod.csv",
    column = "code"
)

# Generic salbutamol DPI inhalers
salbutamol_dpi = codelist_from_csv(
    "codelists/nhs-drug-refsets-gensalbdpinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - Ventolin Evohaler
salbutamol_ventolin_evo = codelist_from_csv(
    "codelists/nhs-drug-refsets-ventevobrdinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - Ventolin Accuhaler
salbutamol_ventolin_accu = codelist_from_csv(
    "codelists/nhs-drug-refsets-ventaccubrdinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - Salbulin Novolizer
salbutamol_salbulin = codelist_from_csv(
    "codelists/nhs-drug-refsets-salbbrdinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - Salamol
salbutamol_salamol = codelist_from_csv(
    "codelists/nhs-drug-refsets-salabrdinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - Easyhaler
salbutamol_easy = codelist_from_csv(
    "codelists/nhs-drug-refsets-easybrdinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - Airomir
salbutamol_airo = codelist_from_csv(
    "codelists/nhs-drug-refsets-airobrdinhdrug_cod.csv",
    column = "code"
)

# Branded salbutamol - AirSalb
salbutamol_airsalb = codelist_from_csv(
    "codelists/nhs-drug-refsets-airsbrdinhdrug_cod.csv",
    column = "code"
)

# all salbutamol codelists
salbutamol = (
    salbutamol_mdi + salbutamol_dpi + salbutamol_ventolin_evo + 
    salbutamol_ventolin_accu + salbutamol_salbulin + salbutamol_salamol +
    salbutamol_easy + salbutamol_airo + salbutamol_airsalb
)

# asthma review
ast_review = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copd_cod.csv",
    column = "code"
)

# ethnicity codes; see category columns here: https://www.opencodelists.org/codelist/opensafely/ethnicity-snomed-0removed/22911876/
ethnicity_codes = codelist_from_csv(
  "codelists/opensafely-ethnicity-snomed-0removed.csv",
  column = "code",
  category_column = "Grouping_6",
)