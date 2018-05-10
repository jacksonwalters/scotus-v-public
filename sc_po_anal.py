#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import numpy as np
import datetime as dt

#global variables
SURVEY_YEAR='VCF0004'
CURRENT_YEAR=2018
SURVEY_YEARS=tuple(set(po_df[SURVEY_YEAR]))
NUM_JUSTICES=9


#get the justice's name given their number
def get_name(num: int) -> str:
    result=list(set(jd_df.loc[jd_df['justice'] == num]['justiceName']))
    if len(result) > 1: return 'NON-UNIQUE'
    if len(result) == 0: return 'FAIL'
    if len(result) == 1: return result[0]

#format entry to be float if possible
def is_num(entry):
    try:
        float(entry)
        return True
    except ValueError:
        return False

#check if the entry is scalable
def scalable(entry,scale=(lambda x: x)):
    if is_num(entry):
        try:
            scale(float(entry))
            return True
        except KeyError:
            return False
    else: return False

#build dict of justice names based on order
#only 113 unique persons have served on the court, however this list
#has 115 index numbers. some assoc. justice were later appointed Chief justice
#seperately, such as Charles Evan Hughes and William Rehnquist.
justice_names={i:get_name(i) for i in range(84,116)}

#fields of interest: caseIssuesId, issue, issueArea. these are id numbers.
#online documentation reveals what they correspond to. create dicts/tables.
issue_areas={1:'Criminal Procedure',2:'Civil Rights',3:'First Amendment',4:'Due Process',5:'Privacy',6:'Attorneys',7:'Unions',8:'Economic Activity',9:'Judicial Power',10:'Federalism',11:'Interstate Relations',12:'Federal Taxation',13:'Miscellaneous',14:'Private Action'} #scraped by hand
issue_df=pd.read_csv('./sc_issues.csv')

#ISSUE=GAY MARRIAGE
############################################################################
############################################################################

#keywords associated with ISSUE
#liberals are supportive of ISSUE
GAY_MAR_KEYWORDS=['gay','lesbian','marriage','same-sex','same sex','homosexual','spouse']
LIB_PRO_ISSUE = True
CONS_PRO_ISSUE = not LIB_PRO_ISSUE

#SUPREME COURT
#############################################################################

#identifiers for RELEVANT CASES from SCDB
#KEY Q: HOW TO GET RELEVANT CASES FROM KEYWORDS
#POTENTIAL A: get natural language description for each case (using API). classify utilizing keywords and SVD.
sc_rel_dates=['6/12/1967','6/30/1986','5/20/1996','6/26/2003','6/26/2013','6/26/2013','6/26/2015'] #DATES NOT UNIQUE INDEX
sc_rel_ids=['1966-119','1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'] #weirdly caseId 1966-199, Loving v. VA is entered twice
sc_rel_names=['LOVING et ux. v. VIRGINIA','BOWERS, ATTORNEY GENERAL OF GEORGIA v. HARDWICK et al.', 'ROY ROMER, GOVERNOR OF COLORADO, et al. v. RICHARD G. EVANS et al.', 'JOHN GEDDES LAWRENCE AND TYRON GARNER v. TEXAS', 'HOLLINGSWORTH v. PERRY', 'UNITED STATES v. WINDSOR', 'OBERGEFELL v. HODGES']
#N.B.: case indices are unique, but only for *case* centered data.
sc_rel_ind=[4255,9086,10940,11870,12983,12985,13161]

#ASSUMPTION: binary variable - "liberals supportive of ISSUE". This means:
# decisionDirection = 1: conservative dir., minVotes = num of supporting votes
# decisionDirection = 2: liberal dir., majVotes = num of supporting votes

#get number of supportive votes given case index
def num_supp_votes(ind):
    case=cd_df.iloc[ind]
    dir=case['decisionDirection']
    if is_num(dir):
        lib_dir = (dir==2)
        cons_dir = not lib_dir
    #case decided in lib. dir., liberals are PRO-ISSUE, supp. votes are maj. votes
    if lib_dir and LIB_PRO_ISSUE: supp_votes = case['majVotes']
    #case decided in lib. dir., conservatives are PRO-ISSUE, supp. votes are maj. votes
    if lib_dir and CONS_PRO_ISSUE: supp_votes = case['minVotes']
    #case decided in cons. dir., liberals are PRO-ISSUE, supp. votes are min. votes
    if cons_dir and LIB_PRO_ISSUE: supp_votes = case['minVotes']
    #case decided in cons. dir., conservatives are PRO-ISSUE, supp. votes are maj. votes
    if cons_dir and CONS_PRO_ISSUE: supp_votes = case['majVotes']
    return supp_votes

#get year case was decided
def case_year(ind):
    case=cd_df.iloc[ind]
    return dt.datetime.strptime(case['dateDecision'],'%m/%d/%Y').year

sc_support={case_year(ind):num_supp_votes(ind)/NUM_JUSTICES for ind in sc_rel_ind}


#PUBLIC OPINION
#########################################################################################

#identifiers for RELEVANT QUESTIONS from ANES PO surveys
po_rel_ques=['VCF0232','VCF0877','VCF0878']

#convert entry to normalized value in [0,1]
#requires maximum value in col, and dict to convert responses to a scale
#default scale is just identity function
def norm(entry,max,scale=(lambda x: x)):
    if scalable(entry,scale): return scale(float(entry))/max
    else: return False

#normalize each entry in a series
def norm_col(col,col_max,scale=(lambda x: x)): return [norm(entry,col_max,scale) for entry in col if scalable(entry,scale)]

#get dict of averages for each column by year
def col_yr_avg(ind,col_max,scale=(lambda x: x)):
    #get relevant question from index
    rel_ques=po_rel_ques[ind]
    #for each survey year, get all data for given question variable
    ques_raw={yr:po_df.loc[po_df[SURVEY_YEAR]==yr][rel_ques] for yr in SURVEY_YEARS}
    #clean and normalize the series data from relevant question col
    ques_norm={yr:norm_col(ques_raw[yr],col_max,scale) for yr in SURVEY_YEARS}
    #average normalized temp for each year
    ques_yr_avg={yr:np.average(ques_norm[yr]) for yr in SURVEY_YEARS if not np.isnan(np.average(ques_norm[yr]))}
    return ques_yr_avg

#question VCF0232 - from ANES "GROUP THERMOMETER: Gays and Lesbians"
#"Gay men and lesbians (that is), homosexuals -- thermometer"
#0-96 temp, 97 unclear, 98=DK, 99=NA, INAP=inappropriate
MAX_TEMP=96
gay_temp_yr_avg=col_yr_avg(0,MAX_TEMP)

#question VCF0877 - from ANES "Strength of Position on Gays in the Military"
#"Do you feel strongly or not strongly that homosexuals should be
#allowed to serve in the United States Armed forces?"
#1 - strongly, allowed  ---> 3
#2 - not strongly, allowed  ---> 2
#4 - not strongly, not be allowed   ---> 1
#5 - strongly, not allowed   ---> 0
#7 - DK if favor or oppose; depends (1988); ---> nan
#9 -  NA if favor or oppose ---> nan
#INAP - inappropriate ---> nan
gay_mil_conv={1:3,2:2,4:1,5:0}
MAX_GAY_MIL=max(gay_mil_conv.values())
gay_mil_scale=(lambda x: gay_mil_conv[x])
gay_mil_yr_avg=col_yr_avg(1,MAX_GAY_MIL,gay_mil_scale)
