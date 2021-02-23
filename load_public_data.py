#PUBLIC OPINION DATA
#ANES time series cumulative data. question surveys to monitor voting,
#public opinion, and political participation in the US from 1948-2016.
#59,944 rows x 1029 columns. ROWS are grouped by YEAR (VCF0004). first few COLS
#represent time and other meta-data, remaining COLS represent responses
#different QUESTIONS.
#roughly 55 million entries

import os
import pandas as pd
from example_issues import civil_rights

#ANES code for survey year
SURVEY_YEAR = 'VCF0004'
#identifiers for RELEVANT QUESTIONS from ANES PO surveys
PO_REL_QUES=list(civil_rights().response_map.keys())

PATH = ".\\data\\anes\\"

#data types
DATA_TYPES_FILENAME = 'data_types.csv'
DATA_TYPES_PATH = os.path.join(PATH,DATA_TYPES_FILENAME)
def anes_data_types():
    #build dict of data types from csv.
    with open(DATA_TYPES_PATH, mode='r') as infile:
        reader = csv.reader(infile)
        data_types = {rows[0]:rows[1] for rows in reader}
    return data_types

#load ANES public opinion data
ANES_DATA_FILENAME = 'anes_timeseries_cdf.dta'
ANES_DATA_PATH = os.path.join(PATH,ANES_DATA_FILENAME)
def anes_opinion_data():
    return pd.read_stata(ANES_DATA_PATH)

#load formatted ANES codebook as df
CODEBOOK_FILENAME = "codebook/formatted_anes_codebook.csv"
CODEBOOK_PATH = os.path.join(PATH,CODEBOOK_FILENAME)
def anes_codebook():
    return pd.read_csv(CODEBOOK_PATH)

if __name__ == "__main__":
    anes_df=anes_data()
    anes_codebook_df=anes_codebook()
    sample_codes = list(anes_codebook_df["vcf_codes"])[:10]
    sample_keys = list(anes_df)[:10]
    print(sample_codes)
    print(sample_keys)
