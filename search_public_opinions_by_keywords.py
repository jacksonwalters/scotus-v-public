import sys, os
import scipy.sparse
import pandas as pd
from load_public_data import anes_opinion_data, anes_codebook
from find_public_opinion_question import find_anes_question

PATH = ".\\data\\tf-idf\\public_opinion\\"

#load tfidf matrix
TFIDF_MATRIX_FILENAME = "tfidf_matrix.npz"
TFIDF_MATRIX_PATH = os.path.join(PATH,TFIDF_MATRIX_FILENAME)
tfidf_matrix = scipy.sparse.load_npz(TFIDF_MATRIX_PATH)
#load {row index : opinion id} mapping
OPINION_ID_FILENAME = "tfidf_rows.csv"
OPINION_ID_PATH = os.path.join(PATH,OPINION_ID_FILENAME)
opin_id_df = pd.read_csv(OPINION_ID_PATH)
opin_id = list(opin_id_df['0'])
#load {col index : vocab} mapping
VOCAB_FILENAME = "tfidf_cols.csv"
VOCAB_PATH = os.path.join(PATH,VOCAB_FILENAME)
vocab_df = pd.read_csv(VOCAB_PATH)
vocab = list(vocab_df['0'])

#find list of relevant cases given set of keywords
#returns list of opinion_ids
def relevant_questions_by_vcf_code(keywords):
    keyword_ind = [vocab.index(keyword) for keyword in keywords if keyword in vocab]

    #score each opinion (row) based on keywords appearing
    #by summing tfidf scores in the relevant columns
    num_questions = tfidf_matrix.shape[0]
    scores = []
    for row in range(num_questions):
        score = sum(tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value, in descending order
    scores.sort(key=lambda tup: tup[1],reverse=True)

    #get relevant questions
    rel_questions = [opin_id[case[0]] for case in scores[:10]]

    return rel_questions

#given keywords, look up relevant questions by searching question text
#and return ANES codebook sub-dataframe
def relevant_questions_anes_df(keywords):
    vcf_codes = relevant_questions_by_vcf_code(keywords) #get opinion ids
    anes_codebook_df = anes_codebook() #get scdb dataframe
    rel_questions = [find_anes_question(vcf_code,anes_codebook_df) for vcf_code in vcf_codes] #get list of scdb cases
    return pd.concat(rel_questions) #concatenate into single df and return


if __name__ == "__main__":
    if(len(sys.argv) > 1):
        keywords = sys.argv[1:]
        print(relevant_questions_anes_df(keywords))
