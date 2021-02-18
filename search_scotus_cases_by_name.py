import pandas as pd
import sys
from example_issues import civil_rights
from load_scotus_data import all_scdb_case_data

#given a word, search all cases and find caseNames which contain the word
#return as a dataframe
def search_scdb_cases_by_name(word,all_cd_df):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

#given a list of case names, print indices of all cases which may be relevant
if __name__ == "__main__":
    print(civil_rights().case_ind)
