import pandas as pd
from load_public_data import anes_opinion_data, classified_questions

#ANES code for survey year
SURVEY_YEAR_VCF_CODE = 'VCF0004'

#get pandas series of averages for each column by year
def scaled_avg_by_year(q_id,rel_ans_df):
    col = rel_ans_df[ [SURVEY_YEAR_VCF_CODE,q_id] ].copy() #get column for q_id. make a deepcopy to avoid reference warnings
    q_orientation = orientation(q_id) #get the LIB/CONS orientation of the question
    resp_conv = resp_convert(q_id,rel_ans_df) #get response conversion dictionary
    magnitude = (lambda x: resp_conv[x] if x in resp_conv.keys() else float('nan')) #create a scale based on conversion dictionary
    polarity = (lambda x: q_orientation*magnitude(x)) #construct a function to use as a conversion scale
    col[q_id] = col[q_id].apply(polarity).astype(float) #scale the column of question responses
    ques_yr_avg = col.groupby([SURVEY_YEAR_VCF_CODE])[q_id].mean() #group by year and average
    return ques_yr_avg #return series of averages for q_id column in rel_ans_df

#PLACEHOLDER. dictionary keeping track of the conversion scales for
#for every response type for PO questions
def resp_convert(q_id,rel_ans_df):
    if rel_ans_df[q_id].dtype.name == "category":
        categories = list(rel_ans_df[q_id].cat.categories) #get ordered list of categories
        resp_dict = {category: 2*(categories.index(category)/(len(categories)-1))-1 for category in categories} #map to [-1,1] based on max/min index
        return resp_dict
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
