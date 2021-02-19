#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import os
import numpy as np
import datetime as dt
from search_scotus_opinions_by_keywords import relevant_cases_scdb_df

#GLOBAL VARIABLES
PLUS_POLE = +1
NO_POLE = 0
MINUS_POLE = -1

#format entry to be float if possible
def is_num(entry):
    try:
        float(entry)
        return True
    except ValueError:
        return False

#(decision direction)*(vote magnitude) for each case
def sc_force(case):
    num_voting_justices = case['minVotes'] + case['majVotes'] #total number of justices
    vote_diff = abs(case['minVotes'] - case['majVotes'])
    vote_mag = vote_diff/num_voting_justices #normalized magnitude of vote force
    return sc_direction(case)*vote_mag

#LIBERAL v. CONSERVATIVE direction of supreme court case
#reference is SCDB codebook
def sc_direction(case):
    dir = case['decisionDirection']
    if is_num(dir):
        if dir==1: #CONSERVATIVE
            return MINUS_POLE
        if dir==2: #LIBERAL
            return PLUS_POLE
        if dir==3: #UNSPECIFIABLE
            return NO_POLE
    else:
        return NO_POLE

#get year case was decided
def case_year(case):
    return dt.datetime.strptime(case['dateDecision'],'%m/%d/%Y').year

#given dataframe of relevant cases, compute vote_ratio*sentiment_direction
#to get polarity for each case
def sc_polarity(relevant_cases):
    return {case_year(case):sc_force(case) for index, case in relevant_cases.iterrows()}

#given relevant cases dataframe, compute polarity by year
if __name__ == "__main__":
    keywords=["gay","marriage","lgbt"]
    rel_cases=relevant_cases_scdb_df(keywords)
    polarity=sc_polarity(rel_cases)
    print(polarity)
