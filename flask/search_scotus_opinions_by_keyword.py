import pandas as pd

#find list of relevant cases given set of keywords
def relevant_cases_by_opin_id(keywords,scotus_vocab,scotus_tfidf_matrix,scotus_opin_id):
    keyword_ind = [scotus_vocab.index(keyword) for keyword in keywords if keyword in scotus_vocab]

    #score each opinion (row) based on keywords appearing
    #by summing tfidf scores in the relevant columns
    num_opinions = scotus_tfidf_matrix.shape[0]
    scores = []
    for row in range(num_opinions):
        score = sum(scotus_tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value, in descending order
    scores.sort(key=lambda tup: tup[1],reverse=True)

    #get relevant cases
    rel_cases = [scotus_opin_id[case[0]] for case in scores[:10]]

    return rel_cases

#given keywords, look up relevant cases by searching opinion text
#match cases to SCDB data and return sub-dataframe
def relevant_cases_scdb_df(keywords,scotus_vocab,scotus_tfidf_matrix,scotus_opin_id,all_scdb_case_data,all_scdb_case_data):
    opin_ids = relevant_cases_by_opin_id(keywords,scotus_vocab,scotus_tfidf_matrix,scotus_opin_id) #get opinion ids
    scdb_cases = [find_scdb_case(opin_id,all_scdb_case_data) for opin_id in opin_ids] #get list of scdb cases
    #if no scdb_cases is empty list
    if not scdb_cases:
        return pd.DataFrame() #return the empty dataframe
    else:
        return pd.concat(scdb_cases) #concatenate the dataframes and return
