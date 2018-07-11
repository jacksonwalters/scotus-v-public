#JACKSON WALTERS
#US SUPREME COURT v. THE COURT OF PUBLIC OPINION
#this project is for The Data Incubator, Summer 2018.
#analyzing relationship between public opinion and supreme court decisions

import numpy as np
import datetime as dt

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
issue_df=pd.read_csv('./scdb/sc_issues.csv')

#SUPREME COURT
#############################################################################

#normalize to be between [-1,+1]
#-1 = force towards minus pole
#0 = no force on the issue
#+1 = force towards plus pole
#requires deciding polarity
def sc_force(id):
    case = cd_df.iloc[id]   #get case
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
    case = cd_df.iloc[id]
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
    case=cd_df.iloc[id]
    return dt.datetime.strptime(case['dateDecision'],'%m/%d/%Y').year

#dict of supreme court polarity by year
sc_support={case_year(id):sc_force(id) for id in sc_rel_ind}


#PUBLIC OPINION
#########################################################################################

#normalize entry to polarization value in [-1,1]
#requires maximum value in col, and dict to convert responses to a scale
#default scale is just identity function
def norm(entry,resp_conv):
    resp_max = max(resp_conv.values())
    scale=(lambda x: resp_conv[x])
    if scalable(entry,scale):
        mag = scale(float(entry))/resp_max   #normalize to [0,1]
        return 2*mag - 1    #map to [-1,1]
    else:
        return float(nan)

#normalize each entry in a series
def norm_col(col,resp_conv):
    scale=(lambda x: resp_conv[x])
    return [norm(entry,resp_conv) for entry in col if scalable(entry,scale)]

#get dict of averages for each column by year
def scaled_avg_by_year(q_id):
    #get column for q_id
    col = rel_po_df[ [SURVEY_YEAR,q_id] ]
    #get appropriate conversion of responses to support values
    resp_conv=resp_convert()[q_id]
    #compute the possible max of all responses
    col_max=max(resp_conv.values())
    #construct a function to use as a conversion scale
    scale=(lambda x: norm(x,resp_conv) )
    #scale the entire column
    #scaled_col = col[q_id].apply(scale,axis=1)
    #separate by year
    #scaled_col.groupby([SURVEY_YEAR])[q_id]


    #for each survey year, get all data for given question variable
    ques_raw={yr:po_df.loc[po_df[SURVEY_YEAR]==yr][q_id] for yr in SURVEY_YEARS}
    #clean and normalize the series data from relevant question col
    ques_norm={yr:norm_col(ques_raw[yr],resp_conv) for yr in SURVEY_YEARS}
    #average normalized temp for each year
    ques_yr_avg={yr:np.average(ques_norm[yr]) for yr in SURVEY_YEARS if not np.isnan(np.average(ques_norm[yr]))}
    return ques_yr_avg

#a dictionary keeping track of the conversion scales for
#for each PO question
def resp_convert():
    return {
        'VCF0232': {i:i for i in range(97)}, #polarity unclear as HOT/COLD is hard to judge
        'VCF0877': {1:3,2:2,4:1,5:0}, #polarity=descending
        'VCF0878': {1:1,5:0}, #polarity=descending
        'VCF0876': {1:1,5:0}, #polarity=descending
        'VCF0876a': {1:4,2:3,4:2,5:1}, #polarity=descending
    }


#AVERAGE PUBLIC OPINION
#########################################################################################

#build dict of overall averages.
#COULD USE MapReduce HERE.
all_po_avg={}
for q_id in po_rel_ques:
    #compute average of column for question id q_id
    col_avg = scaled_avg_by_year(q_id)
    #append each value in the dictonary to the appropirate key
    for key,value in col_avg.items():
        if key in all_po_avg.keys():
            all_po_avg[key] += [value]
        else:
            all_po_avg[key] = [value]

#reduce by averaging each list of col averages
all_po_avg = {key:np.average(all_po_avg[key]) for key in all_po_avg.keys()}
