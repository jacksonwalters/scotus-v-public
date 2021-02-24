from random import choice
from search_public_opinions_by_keywords import relevant_questions_anes_df
from load_public_data import anes_opinion_data
from example_issues import civil_rights

#ANES code for survey year
SURVEY_YEAR = 'VCF0004'
#identifiers for RELEVANT QUESTIONS from ANES PO surveys
EX_PO_REL_QUES = list(civil_rights().response_map.keys())

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
    high = max(resp_conv.values())
    low = min(resp_conv.values())
    max_mag = max(abs(high),abs(low))
    scale=(lambda x: resp_conv[x])
    if scalable(entry,scale):
        return scale(float(entry))/max_mag   #normalize to [-1,1]
    else:
        return float('nan')

#normalize each entry in a series
def norm_col(col,resp_conv):
    scale=(lambda x: resp_conv[x])
    return [norm(entry,resp_conv) for entry in col if scalable(entry,scale)]

#get dict of averages for each column by year
def scaled_avg_by_year(q_id,rel_ans_df):
    #get column for q_id
    col = rel_ans_df[ [SURVEY_YEAR,q_id] ]
    print(col)
    #get appropriate conversion of responses to support values
    resp_conv=resp_convert()[q_id]
    #compute the possible max of all responses
    col_max=max(resp_conv.values())
    #construct a function to use as a conversion scale
    scale=(lambda x: norm(x,resp_conv) )
    #scale the column of question responses
    col[q_id] = col[q_id].apply(scale)
    #group by year and average
    ques_yr_avg=col.groupby([SURVEY_YEAR])[q_id].mean()

    return ques_yr_avg

#dictionary keeping track of the conversion scales for
#for every response type for PO questions
def resp_convert():
    return dict()

#given a PO question, determine whether an affirmative response would be
#considered LIBERAL or CONSERVATIVE. this is a binary classifier which
#can be implemented as a trained neural network, a CNN. likely will just
#append YES or NO to the question and apply a sigmoid to the output of a sentiment
#analyzer. for now, it is a placeholder
def orientation(question):
    return choice([-1,+1])

#return {year:polarity} dict for public opinion
def public_polarity(rel_ques_df,rel_ans_df):
    #get keys for relevant questions as VCF codes
    po_rel_ques_keys = list(rel_ques_df['vcf_code'])
    print(po_rel_ques_keys)
    #for each question key, avgerage the responses from that column
    po_q_avgs = [scaled_avg_by_year(q_id,rel_ans_df) for q_id in po_rel_ques_keys] #collect avg's for all Q's
    print(po_q_avgs)
    """
    po_q_avgs_df = pd.concat(po_q_avgs,axis=1) #join series into df
    po_avgs_df = po_q_avgs_df.mean(axis=1) #take row mean
    po_avgs_df = po_avgs_df.loc[ po_avgs_df.notna() ] #remove NaN's
    po_polarity = po_avgs_df.to_dict() #go from df to dictionary
    """
    return dict()

#run a sample test
if __name__ == "__main__":
    keywords=["gay","marriage","lgbt","rights","sodomy"] #example keywords
    #search the relevant q's & return ANES codebook sub-df
    rel_ques_df = relevant_questions_anes_df(keywords)
    rel_vcf_codes = [SURVEY_YEAR]+list(rel_ques_df['vcf_code'])
    #load the full ANES response data. should be trimmed to *relevant dataframe*
    anes_df = anes_opinion_data()
    #filter the relevant repsonses/answers by VCF code
    rel_ans_df = anes_df.filter(items=rel_vcf_codes)
    #compute polarity for relevant questions
    polarity=public_polarity(rel_ques_df,rel_ans_df)
    print(polarity)
