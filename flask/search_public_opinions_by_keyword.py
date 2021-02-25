import pandas as pd

#find list of relevant cases given set of keywords
#returns list of vcf codes for public opinion
def relevant_questions_by_vcf_code(keywords,public_vocab,public_tfidf_matrix,public_opin_id):
    keyword_ind = [public_vocab.index(keyword) for keyword in keywords if keyword in public_vocab]

    #score each opinion (row) based on keywords appearing
    #by summing tfidf scores in the relevant columns
    num_questions = public_tfidf_matrix.shape[0]
    scores = []
    for row in range(num_questions):
        score = sum(public_tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value, in descending order
    scores.sort(key=lambda tup: tup[1],reverse=True)

    #get relevant questions
    rel_questions = [public_opin_id[case[0]] for case in scores[:10]]

    return rel_questions

#given keywords, look up relevant questions by searching question text
#and return ANES codebook sub-dataframe
def relevant_questions_anes_df(keywords,public_vocab,public_tfidf_matrix,public_opin_id,anes_codebook_df):
    vcf_codes = relevant_questions_by_vcf_code(keywords,public_vocab,public_tfidf_matrix,public_opin_id) #get public opinion vcf codes
    rel_questions = [find_anes_question(vcf_code,anes_codebook_df) for vcf_code in vcf_codes] #get list of public opinion questions
    #if there are no relevant questions, return the empty dataframe
    if not rel_questions:
        return pd.DataFrame()
    else:
        return pd.concat(rel_questions) #concatenate into single df and return
