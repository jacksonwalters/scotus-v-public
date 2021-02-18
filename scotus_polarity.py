#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import os
import numpy as np
import datetime as dt

#GLOBAL VARIABLES
PLUS_POLE = +1
MINUS_POLE = -1
NO_POLE = 0
CURRENT_YEAR=2018
NUM_JUSTICES=9
NEUTRAL = 0 #the line deciding which side of the issue

#format entry to be float if possible
def is_num(entry):
    try:
        float(entry)
        return True
    except ValueError:
        return False

#get the justice's name given their number
def get_name(num: int) -> str:
    result=list(set(jd_df.loc[jd_df['justice'] == num]['justiceName']))
    if len(result) > 1: return 'NON-UNIQUE'
    if len(result) == 0: return 'FAIL'
    if len(result) == 1: return result[0]

#build dict of justice names based on order
#only 113 unique persons have served on the court, however this list
#has 115 index numbers. some assoc. justice were later appointed Chief justice
#seperately, such as Charles Evan Hughes and William Rehnquist.
justice_names={i:get_name(i) for i in range(84,116)}

#normalize to be between [-1,+1]
#-1 = force towards minus pole
#0 = no force on the issue
#+1 = force towards plus pole
#requires deciding polarity
def sc_force(id):
    case = all_cd_df.iloc[id]   #get case
    num_justices = case['minVotes'] + case['majVotes'] #total number of justices
    polarity = sc_direction(id)  #determine polarity/direction of decision
    vote_diff = abs(case['minVotes'] - case['majVotes'])
    vote_mag = vote_diff/num_justices #normalized magnitude of vote force

    if polarity == PLUS_POLE:
        return PLUS_POLE*vote_mag
    elif polarity == MINUS_POLE:
        return MINUS_POLE*vote_mag
    elif polarity == NO_POLE:
        return NO_POLE*vote_mag

#polarity of supreme court case.
#use decision direction column to decide
#liberal vs conservative.
def sc_direction(id):
    case = all_cd_df.iloc[id]
    dir = case['decisionDirection']
    if is_num(dir):
        if dir==2:
            return PLUS_POLE
        if dir==1:
            return MINUS_POLE
    else:
        return NO_POLE

#get year case was decided
def case_year(id):
    case=all_cd_df.iloc[id]
    return dt.datetime.strptime(case['dateDecision'],'%m/%d/%Y').year

#dict of supreme court polarity by year
sc_polarity={case_year(id):sc_force(id) for id in SC_REL_IND}
