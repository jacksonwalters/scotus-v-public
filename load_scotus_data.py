#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import pandas as pd
import csv, os

PATH = ".\\data\\scdb\\"
#path for scotus case data from SCDB, 1946 - present
SCOTUS_CASE_DATA_FILENAME = 'scdb_case_data.csv'
CASE_DATA_PATH = os.path.join(PATH,SCOTUS_CASE_DATA_FILENAME)
#path for scotus legacy case data from SCDB, 1789 - 1946
SCOTUS_LEGACY_CASE_DATA_FILENAME = 'scdb_legacy_case_data.csv'
LEGACY_CASE_DATA_PATH = 'scdb_legacy_case_data.csv'

#GLOBAL VARIABLES
PLUS_POLE = 1
MINUS_POLE = -1
NO_POLE = 0
CURRENT_YEAR=2018
NUM_JUSTICES=9
NEUTRAL = 0 #the line deciding which side of the issue

ISSUE_NAME=CIVIL_RIGHTS_NAME
KEYWORDS=CIVIL_RIGHTS_KEYWORDS

RESP_CONVERT=CIVIL_RIGHTS_RESPONSE_MAP

#COMPUTED FROM INPUT
SC_REL_IND=CIVIL_RIGHTS_IND

def load_scotus_data():
    #load csv files with pandas. not utf-8, must use alternate encoding
    #case centered data stored in dataframe
    cd_df=pd.read_csv(CASE_DATA_PATH,encoding='windows-1252')
    cd_legacy_df=pd.read_csv(LEGACY_CASE_DATA_PATH,encoding='windows-1252')

    cd_dfs=[cd_legacy_df,cd_df]
    #merge case centered dataframes making sure to keep a unique numeric index
    all_cd_df = pd.concat(cd_dfs,ignore_index=True)
    rel_cd_cases = all_cd_df.iloc[SC_REL_IND] #only need relevant SC cases

    #justice (the SC justice as a person) centered data stored in dataframe
    #justice data is a superset of case data and gives info about how
    #each particular jusitce voted.
    jd_df=pd.read_csv('~/Data/scvpo/scdb_justice_data.csv',encoding='windows-1252')
    jd_legacy_df=pd.read_csv('~/Data/scvpo/scdb_legacy_case_data.csv',encoding='windows-1252')

    #relevant justice data
    jd_dfs=[jd_df,jd_legacy_df]
    all_jd_df = pd.concat(jd_dfs) #merge justice centered dataframes
    rel_jd_cases = all_jd_df.iloc[SC_REL_IND] #only need relevant cases

#load supreme court data
if __name__ == "__main__":
    load_scotus_data()
