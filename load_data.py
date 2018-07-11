#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import pandas as pd
import csv

#GLOBAL VARIABLES
SURVEY_YEAR = 'VCF0004'
PLUS_POLE = 1
MINUS_POLE = -1
NO_POLE = 0
CURRENT_YEAR=2018
NUM_JUSTICES=9

#USER INPUT
######################################################################

ISSUE_NAME="Same-Sex Marriage"
GAY_MAR_KEYWORDS=['gay','lesbian','marriage','same-sex','same sex','homosexual','spouse']


#COMPUTED FROM INPUT
#identifiers for RELEVANT CASES from SCDB
#KEY Q: HOW TO GET RELEVANT CASES FROM KEYWORDS
#A: scrape opinion text from web or load into db. classify utilizing keywords and tfidf.
sc_rel_ids=['1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'] #weirdly caseId 1966-119, Loving v. VA is entered twice
#N.B.: case indices are unique, but only for *case* centered data.
sc_rel_ind=[9086,10940,11870,12983,12985,13161]

#identifiers for RELEVANT QUESTIONS from ANES PO surveys
#these should be computed from keyword set input
po_rel_ques=['VCF0232','VCF0877','VCF0878','VCF0876','VCF0876a']

#DATA
######################################################################

#SUPREME COURT DATA
#load csv files with pandas. not utf-8, must use alternate encoding
#case centered data stored in dataframe
cd_df=pd.read_csv('~/Data/scvpo/scdb_case_data.csv',encoding='windows-1252')
cd_legacy_df=pd.read_csv('~/Data/scvpo/scdb_legacy_case_data.csv',encoding='windows-1252')

cd_dfs=[cd_df,cd_legacy_df]
all_cd_df = pd.concat(cd_dfs) #merge case centered dataframes
rel_cd_cases = all_cd_df.iloc[sc_rel_ind] #only need relevant SC cases

#justice (the SC justice as a person) centered data stored in dataframe
#justice data is a superset of case data and gives info about how
#each particular jusitce voted.
jd_df=pd.read_csv('~/Data/scvpo/scdb_justice_data.csv',encoding='windows-1252')
jd_legacy_df=pd.read_csv('~/Data/scvpo/scdb_legacy_case_data.csv',encoding='windows-1252')

#relevant justice data
jd_dfs=[jd_df,jd_legacy_df]
all_jd_df = pd.concat(jd_dfs) #merge justice centered dataframes
rel_jd_cases = all_jd_df.iloc[sc_rel_ind] #only need relevant cases

#PUBLIC OPINION DATA
#ANES time series cumulative data. question surveys to monitor voting,
#public opinion, and political participation in the US from 1948-2016.
#55674 rows x 952 columns. ROWS are grouped by YEAR (VCF0004). first few COLS
#represent time and other meta-data, remaining COLS represent responses
#different QUESTIONS.
#roughly 55 million entries

#build dict of data types from csv.
with open('./anes/data_types.csv', mode='r') as infile:
    reader = csv.reader(infile)
    data_types = {rows[0]:rows[1] for rows in reader}

po_df=pd.read_csv('~/Data/scvpo/anes_data.csv')
rel_po_df = po_df[po_rel_ques] #only use relevant public opinion questions

SURVEY_YEARS=tuple(set(po_df[SURVEY_YEAR]))
