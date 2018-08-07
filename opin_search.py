lgbt_keywords={'gay','lesbian','sodomy','marraige','homosexual'}

#SHOULD IMPLEMENT ONLY USING SPARSE MATRICES

#find list of relevant cases given set of keywords
def relevant_cases(keywords):
    keyword_ind = [feature_names.index(keyword) for keyword in keywords if keyword in feature_names]

    #score each opinion based on keywords appearing
    scores = []
    for row in range(tfidf_matrix.shape[0]):
        score = sum(tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value
    scores.sort(key=lambda tup: tup[1])

    return scores
