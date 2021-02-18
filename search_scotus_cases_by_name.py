import pandas as pd
import sys
from example_issues import civil_rights
from load_scotus_data import all_scdb_case_data

#load all (legacy+modern) SCOTUS case data
all_cd_df = all_scdb_case_data()

#given a word, search all cases and find caseNames which contain the word
#return as a dataframe
def search_scdb_cases_by_name(word):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

#given a case name, return the index in the list of all cases (legacy+modern)
def sc_find_case(name):
    upper=str.upper(name) #convert name to upper case
    words=upper.split() #split case name into list of words
    #the last word is (YEAR), e.g. DOGS V. CATS (1836)
    year=int(words.pop().strip("()"))
    #join the words again w/spaces between, and split in two on V.
    #e.g. ['DOGS','V.','CATS'] --> "DOGS V. CATS" --> ['DOGS','CATS']
    partys=" ".join(words).split("V.")

    #get both parties
    party1=words[0].strip()
    party2=words[1].strip()

    df1=search_scdb_cases_by_name(party1) #get dataframe of cases containing party1 in name
    index1=set(list(df1.index)) #get indices of cases within df of all cases

    df2=search_scdb_cases_by_name(party2) #get dataframe of cases containing party2 in name
    index2=set(list(df2.index)) #get indices of cases within df of all cases

    #keep cases in which party appears in both
    result = index1.intersection(index2)

    return result

#dict of indices for each case name, i.e. {"name of SCOTUS case":[indices in SCDB case df]}
def possible_case_indices(names):
    return {name:sc_find_case(name) for name in names}

#given a list of case names, print indices of all cases which may be relevant
if __name__ == "__main__":
    possible_indices = possible_case_indices(civil_rights().scotus_cases)
    indices = set()
    for index_set in possible_indices.values():
        indices = indices.union(index_set)
    print(indices)

    print(civil_rights().case_ind)
