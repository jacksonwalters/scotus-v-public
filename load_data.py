#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import pandas as pd
import csv

#DATA
######################################################################
#load csv files with pandas. not utf-8, must use alternate encoding
#case centered data stored in dataframe
cd_df=pd.read_csv('./scdb/scdb_case_data.csv',encoding='windows-1252')
#justice (the SC justice as a person) centered data stored in dataframe
#justice data is a superset of case data and gives info about how
#each particular jusitce voted.
jd_df=pd.read_csv('./scdb/scdb_justice_data.csv',encoding='windows-1252')

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

po_df=pd.read_csv('./anes/anes_data.csv')
