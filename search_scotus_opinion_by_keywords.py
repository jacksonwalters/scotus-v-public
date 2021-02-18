import sys, os
import scipy.sparse
import pandas as pd

PATH = ".\\data\\"
#path for tf-idf matrix
TDIDF_MATRIX_FILENAME = "tfidf_matrix.npz"
TFIDF_MATRIX_PATH = os.path.join(PATH,TFIDF_MATRIX_FILENAME)
#path for opinion ids, rows of tf-idf matrix
OPINION_ID_FILENAME = "tfidf_rows.csv"
OPINION_ID_PATH = os.path.join(PATH,OPINION_ID_FILENAME)
#path for corpus vocabular, cols of tf-idf matrix
VOCAB_FILENAME = "tfidf_cols.csv"
VOCAB_PATH = os.path.join(PATH,VOCAB_FILENAME)

#load tfidf matrix
tfidf_matrix = scipy.sparse.load_npz(TFIDF_MATRIX_PATH)
#load {row index : opinion id} mapping
opin_id_df = pd.read_csv(OPINION_ID_PATH)
opin_id = list(opin_id_df['0'])
#load {col index : vocab} mapping
vocab_df = pd.read_csv(VOCAB_PATH)
vocab = list(vocab_df['0'])

#find list of relevant cases given set of keywords
def relevant_cases(keywords):
    keyword_ind = [vocab.index(keyword) for keyword in keywords if keyword in vocab]

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

    #get relevant cases
    rel_cases = [opin_id[case[0]] for case in scores[:10]]

    return rel_cases

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        keywords = sys.argv[1:]
        print(relevant_cases(keywords))
