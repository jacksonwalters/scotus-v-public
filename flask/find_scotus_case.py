import pandas as pd

#given a word, search all cases and find caseNames which contain the word
#return as a dataframe
def search_scdb_cases_by_name(word,all_scdb_case_data):
    return all_scdb_case_data[all_scdb_case_data['caseName'].str.contains(word,na=False)]

#try to convert case names from SCDB 'caseName' field to CL opinion scraped
#casenames. cl_opin case_names are from urls, so lowercase smashed w/ hyphens
#vs,versus -> v
def format_case_name(case_name):
    return str(case_name).lower().lstrip().rstrip().replace(',','').replace("'",'').replace('versus','v').replace('vs.','v.').replace('.','').replace(' ','-')

#find case in SCDB database given CourtListener opinion_id
#CL ids are in form "U.S. citation|lower-case-v-name"
def find_scdb_case(cl_opin_id,all_scdb_case_data):
    us_citation = cl_opin_id.split('|')[0]
    #get df of all cases with given U.S. citation "xxx U.S. xxx"
    scdb_cases = all_scdb_case_data[all_scdb_case_data['usCite']==us_citation]
    if not scdb_cases.empty:
        return scdb_cases
    #if that doesn't work, try lower-case-v-name
    case_name_from_id = cl_opin_id.split('|')[1]
    for caseName in all_scdb_case_data['caseName']:
        if format_case_name(case_name_from_id) == format_case_name(caseName):
            return all_scdb_case_data[all_scdb_case_data['caseName']==caseName]
    #if no match, return the empty DataFrame
    return pd.DataFrame()
