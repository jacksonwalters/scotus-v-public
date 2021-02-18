import pandas as pd
import sys
from example_issues import civil_rights
from load_scotus_data import all_scdb_case_data

#given caseName from SCDB database, use as key to look up cases in CL opinion database
#Dogs v. Cats (1941) --> dogs-v-cats.
#WARNING: not a perfect mapping, and often 1:2 due to dissenting opinions
def scotus_opinion_key(scdb_caseName):
    return scdb_caseName.replace(' ','-').replace('.','').lower()

#given a word, search all cases and find caseNames which contain the word
#return as a dataframe
def search_scdb_cases_by_name(word,all_cd_df):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]



#given a list of case names, print indices of all cases which may be relevant
if __name__ == "__main__":
    print(civil_rights().case_ind)
