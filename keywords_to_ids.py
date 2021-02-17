import pandas as pd
import sys
from example_issues import civil_rights
from load_scotus_data import all_scdb_case_data

#load all (legacy+modern) SCOTUS case data
all_cd_df = all_scdb_case_data()

#given a word, search all cases
def search(word):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

#given a case name, return the index in the list of all cases (legacy+modern)
def sc_find_case(name):
    upper=str.upper(name) #convert name to upper case
    words=upper.split() #split case name into list of words
    year=int(words.pop().strip("()")) #the last word is (YEAR)
    words=" ".join(words).split("V.") #join the words again, but split in two on V.

    #should search for all words in each party name
    party1=words[0].strip()
    party2=words[1].strip()

    df1=search(party1)
    index1=set(list(df1.index))

    df2=search(party2)
    index2=set(list(df2.index))

    result = sorted(list(index1.intersection(index2)))

    return result

def possible_ids():
    return {name:sc_find_case(name) for name in civil_rights().scotus_cases}

if __name__ == "__main__":
    print(possible_ids())
    print(civil_rights().case_ind)
