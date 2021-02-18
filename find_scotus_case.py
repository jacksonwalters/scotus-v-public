import pandas as pd
import sys
from example_issues import civil_rights

#given a word, search all cases and find caseNames which contain the word
#return as a dataframe
def search_scdb_cases_by_name(word,all_scdb_case_data):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

#try to convert case names from SCDB 'caseName' field to CL opinion scraped
#casenames. cl_opin case_names are from urls, so lowercase smashed w/ hyphens
#vs,versus -> v
def cl_opin_case_name(scdb_caseName):
    return str(scdb_caseName).lower().replace(',','').replace("'",'').replace(' ','-').replace('versus','v').replace('vs','v')

#find case in SCDB database given CourtListener opinion_id
#CL ids are in form "U.S. citation|lower-case-v-name"
def find_scdb_case(cl_opin_id,all_scdb_case_data):
    us_citation = cl_opin_id.split('|')[0]
    case_name = cl_opin_id.split('|')[1]

    #get df of all cases with given U.S. citation "xxx U.S. xxx"
    scdb_cases = all_scdb_case_data[all_scdb_case_data['usCite']==us_citation]
    if not scdb.empty:
        return scdb_cases
    #if that doesn't work, try lower-case-v-name
    for caseName in all_scdb_case_data['caseNames']:
        if case_name == cl_opin_case_name(caseName):
            all_scdb_case_data[all_scdb_case_data['caseName']==caseName]

#given a list of case names, print indices of all cases which may be relevant
if __name__ == "__main__":
    print(civil_rights().case_ind)
