from search_public_opinions_by_keywords import relevant_questions_anes_df

#check if the entry is scalable
def scalable(entry,scale=(lambda x: x)):
    if is_num(entry):
        try:
            scale(float(entry))
            return True
        except KeyError:
            return False
    else: return False

#normalize entry to polarization value in [-1,1]
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
def scaled_avg_by_year(q_id):
    #get column for q_id
    col = rel_po_df[ [SURVEY_YEAR,q_id] ]
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

#a dictionary keeping track of the conversion scales for
#for each PO question
def resp_convert():
    return dict()

#return {year:polarity} dict for public opinion
def public_polarity(relevant_questions):
    """
    po_q_avgs = [scaled_avg_by_year(q_id) for q_id in PO_REL_QUES] #collect avg's for all Q's
    po_q_avgs_df = pd.concat(po_q_avgs,axis=1) #join series into df
    po_avgs_df = po_q_avgs_df.mean(axis=1) #take row mean
    po_avgs_df = po_avgs_df.loc[ po_avgs_df.notna() ] #remove NaN's
    po_polarity = po_avgs_df.to_dict() #go from df to dictionary
    """
    return dict()

if __name__ == "__main__":
    keywords=["gay","marriage","lgbt","rights","sodomy"]
    rel_questions=relevant_questions_anes_df(keywords)
    polarity=public_polarity(rel_questions)
    print(polarity)
