#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import numpy as np
import matplotlib.pyplot as plt

#global name for variable corresponding to year of survey
SURVEY_YEAR='VCF0004'
SURVEY_YEARS=list(set(po_df[SURVEY_YEAR]))

#the headers which are in justice data and not in case data
in_j_not_c=[x for x in list(jd_df) if x not in list(cd_df)]

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

#fields of interest: caseIssuesId, issue, issueArea. these are id numbers.
#online documentation reveals what they correspond to. create dicts/tables.
issue_areas={1:'Criminal Procedure',2:'Civil Rights',3:'First Amendment',4:'Due Process',5:'Privacy',6:'Attorneys',7:'Unions',8:'Economic Activity',9:'Judicial Power',10:'Federalism',11:'Interstate Relations',12:'Federal Taxation',13:'Miscellaneous',14:'Private Action'}
issue_df=pd.read_csv('./sc_issues.csv')

#ISSUE=GAY MARRIAGE
############################################################################

#keywords associated with ISSUE
gay_mar_keywords=['gay','lesbian','marriage','same-sex','same sex','homosexual','spouse']

#identifiers for RELEVANT CASES from SCDB
#KEY Q: HOW TO GET RELEVANT CASES FROM KEYWORDS
#POTENTIAL A: get natural language description for each case (using API). classify utilizing keywords and SVD.
sc_rel_dates=['6/12/1967','6/30/1986','5/20/1996','6/26/2003','6/26/2013','6/26/2013','6/26/2015'] #DATES NOT UNIQUE INDEX
sc_rel_ids=['1966-119','1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'] #weirdly caseId 1966-199, Loving v. VA is entered twice
sc_rel_names=['LOVING et ux. v. VIRGINIA','BOWERS, ATTORNEY GENERAL OF GEORGIA v. HARDWICK et al.', 'ROY ROMER, GOVERNOR OF COLORADO, et al. v. RICHARD G. EVANS et al.', 'JOHN GEDDES LAWRENCE AND TYRON GARNER v. TEXAS', 'HOLLINGSWORTH v. PERRY', 'UNITED STATES v. WINDSOR', 'OBERGEFELL v. HODGES']
sc_rel_ind=[4255,9086,10940,11870,12983,12985,13161]

#identifiers for RELEVANT QUESTIONS from ANES PO surveys
po_rel_ques=['VCF0232','VCF0877','VCF0878']

#convert entry to normalized value in [0,1]
def norm(entry,max):
    if isinstance(entry, int) and entry <= max: return entry/max
    if isinstance(entry, float) and entry<=max: return entry/max
    if isinstance(entry, str) and entry != '  ' and float(entry)<=max: return float(entry)/max
    else: return False

#question VCF0232 - from ANES "GROUP THERMOMETER: Gays and Lesbians"
#0-96 temp, 97 unclear, 98=DK, 99=NA, INAP=inappropriate
MAX_TEMP=96

#normalize each entry in a series
def norm_col(series,max): return [norm(raw_temp,max) for raw_temp in series if norm(raw_temp,max)]

#for each survey year, get all data for given question variable
gay_temp_raw={yr:po_df.loc[po_df[SURVEY_YEAR]==yr][po_rel_ques[0]] for yr in SURVEY_YEARS}

#clean and normalize the series data from relevant question col
gay_temp_norm={yr:norm_col(gay_temp_raw[yr],MAX_TEMP) for yr in SURVEY_YEARS}

#average normalized temp for each year
gay_temp_yr_avg={yr:np.average(gay_temp_norm[yr]) for yr in SURVEY_YEARS if not np.isnan(np.average(gay_temp_norm[yr]))}

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
MAX_GAY_MIL=3

plt.plot(gay_temp_yr_avg.keys(),gay_temp_yr_avg.values())
