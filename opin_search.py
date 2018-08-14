import scipy.sparse

#load tfidf matrix
tfidf_matrix = scipy.sparse.load_npz("/Users/jackson/Data/scvpo/tfidf_matrix.npz")

#find list of relevant cases given set of keywords
def relevant_cases(keywords):
    keyword_ind = [feature_names.index(keyword) for keyword in keywords if keyword in feature_names]

    #score each opinion (row) based on keywords appearing
    #by summing tfidf scores in the relevant columns
    num_opinions = tfidf_matrix.shape[0]
    scores = []
    for row in range(num_opinions):
        score = sum(tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value, in descending order
    scores.sort(key=lambda tup: tup[1],reverse=True)

    return scores
