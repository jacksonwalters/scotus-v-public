#PUBLIC OPINION DATA
#ANES time series cumulative data. question surveys to monitor voting,
#public opinion, and political participation in the US from 1948-2016.
#59,944 rows x 1029 columns. ROWS are grouped by YEAR (VCF0004). first few COLS
#represent time and other meta-data, remaining COLS represent responses
#different QUESTIONS.
#roughly 55 million entries

import os
import pandas as pd

PATH = ".\\data\\anes\\"

#load ANES public opinion data
ANES_DATA_PATH = os.path.join(PATH,'anes_timeseries_cdf.dta')
def anes_opinion_data():
    return pd.read_stata(ANES_DATA_PATH)

#load formatted ANES codebook as df
CODEBOOK_PATH = os.path.join(PATH,"codebook/formatted_anes_codebook.csv")
def anes_codebook():
    return pd.read_csv(CODEBOOK_PATH)

#load list of {-1,0,+1} classified questions as df
CLASSIFIED_QUES_PATH = os.path.join(PATH,"classified_questions.csv")
def classified_questions():
    return pd.read_csv(CLASSIFIED_QUES_PATH,index_col='vcf_code')

#run a sample test
if __name__ == "__main__":
    #load data
    anes_opinion_df=anes_opinion_data()
    anes_codebook_df=anes_codebook()
    anes_class_ques_df=classified_questions()
    #choose sample subsets
    sample_codes = list(anes_codebook_df["vcf_code"])[:10]
    sample_keys = list(anes_opinion_df)[:10]
    sample_classified_ques = list(anes_class_ques_df["ques_class"][200:300])
    #print samples
    print(sample_codes)
    print(sample_keys)
    print(sample_classified_ques)
    #print memory usage of data
    print(anes_opinion_df.memory_usage(index=False, deep=True))
    print(anes_codebook_df.memory_usage(index=False, deep=True))
    print(anes_class_ques_df.memory_usage(index=False, deep=True))
