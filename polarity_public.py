import pandas as pd
from random import choice
from search_public_opinions_by_keywords import relevant_questions_anes_df
from load_public_data import anes_opinion_data, classified_questions
from example_issues import civil_rights

#ANES code for survey year
SURVEY_YEAR_VCF_CODE = 'VCF0004'
#identifiers for RELEVANT QUESTIONS from ANES PO surveys
EX_PO_REL_QUES = list(civil_rights().response_map.keys())

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

#normalize entry to value in [-1,1]
#requires maximum value in col, and dict to convert responses to a scale
#default scale is just identity function
def norm(entry,resp_conv):
    high = max(resp_conv.values()) #get maximum value of response conversion dict
    low = min(resp_conv.values()) #get minimum value of response conversion dict
    max_mag = max(abs(high),abs(low))  #find absolute max of high & low values
    scale=(lambda x: resp_conv[x] if x in resp_conv.keys() else 0) #create a scale based on conversion dictionary
    if scalable(entry,scale): #check if the entry can be scaled at all
        return scale(float(entry))/max_mag if max_mag != 0 else 0  #normalize to [-1,1]
    else:
        return float('nan')

#get pandas series of averages for each column by year
def scaled_avg_by_year(q_id,rel_ans_df):
    col = rel_ans_df[ [SURVEY_YEAR_VCF_CODE,q_id] ].copy() #get column for q_id. make a deepcopy to avoid reference warnings
    resp_conv=resp_convert(q_id) #get response conversion dictionary
    scale=(lambda x: orientation(q_id)*norm(x,resp_conv)) #construct a function to use as a conversion scale
    col[q_id] = col[q_id].apply(scale) #scale the column of question responses
    ques_yr_avg=col.groupby([SURVEY_YEAR_VCF_CODE])[q_id].mean() #group by year and average
    return ques_yr_avg #return series of averages for q_id column in rel_ans_df

#PLACEHOLDER. dictionary keeping track of the conversion scales for
#for every response type for PO questions
def resp_convert(q_id):
    return {"":0}

#PLACEHOLDER. given a PO question, determine whether an affirmative response would be
#considered LIBERAL or CONSERVATIVE. this is a binary classifier which
#can be implemented as a trained neural network, a CNN. likely will just
#append YES or NO to the question and apply a sigmoid to the output of a sentiment
#analyzer. for now, it is a placeholder
def orientation(q_id):
    class_ques_df = classified_questions()
    return class_ques_df.loc[q_id,'ques_class']

#PLACEHOLDER. analyze the polarity of a question+answer/response.
#merge the question and answer into a statement, and run through
#sentiment analyzer CNN and return a number in [-1,+1] where
#-1 represents conservative and +1 represents liberal (arbitrary)
def sentiment(question,answer):
    statement = question + answer
    return int("liberal" in statement)

#return {year:polarity} dict for public opinion
def po_polarity(rel_ques_df,rel_ans_df):
    po_rel_ques_keys = list(rel_ques_df['vcf_code']) #get keys for relevant questions as VCF codes
    po_q_avgs = [scaled_avg_by_year(q_id,rel_ans_df) for q_id in po_rel_ques_keys] #for each relevant question key, avg responses from column by year
    po_q_avgs_df = pd.concat(po_q_avgs,axis=1) #join list of series into df
    po_avgs_df = po_q_avgs_df.mean(axis=1) #take row mean
    po_avgs_df = po_avgs_df.loc[ po_avgs_df.notna() ] #remove NaN's
    po_polarity = po_avgs_df.to_dict() #go from df to dictionary
    return po_polarity #return dict of PO polarity

#run a sample test
if __name__ == "__main__":
    keywords=["gay","marriage","lgbt","rights","sodomy"] #example keywords
    rel_ques_df = relevant_questions_anes_df(keywords) #search the relevant q's & return ANES codebook sub-df
    rel_vcf_codes = [SURVEY_YEAR_VCF_CODE]+list(rel_ques_df['vcf_code']) #list of relevant vcf_code keys including code for question year
    anes_df = anes_opinion_data() #load the full ANES response data
    rel_ans_df = anes_df.filter(items=rel_vcf_codes) #filter the relevant repsonses/answers by VCF code
    polarity=po_polarity(rel_ques_df,rel_ans_df) #dict {year:polarity} for public opinion
    print(polarity)
