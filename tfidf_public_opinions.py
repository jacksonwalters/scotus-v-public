import os, math
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse
from load_public_data import anes_opinion_data, anes_codebook

#output paths
DATA_PATH = ".\\data\\tf-idf\\public_opinion\\"
TFIDF_MATRIX_PATH = os.path.join(DATA_PATH,'tfidf_matrix.npz') #tf-idf matrix filepath
TFIDF_ROWS_PATH = os.path.join(DATA_PATH,"tfidf_rows.csv") #opin ids filepath
TFIDF_COLS_PATH = os.path.join(DATA_PATH,"tfidf_cols.csv") #vocab filepath

#perform a TF-IDF analysis on corpus of opinion text data
def tfidf_opins():
    #store opinion data as dataframe
    opin_df = anes_codebook()

    #generate corpus
    corpus=[]
    for opin in list(opin_df['question']):
        try:
            if math.isnan(opin):
                corpus.append("")
        except TypeError:
            opin_text = str(opin)
            corpus.append(opin_text)

    #generate tfidf matrix. set maximum document freq. and minimum cut-off to limit dumb non-words
    max_n=2 #specify maximum n-gram size (length of phrases)
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1,max_n), stop_words="english", min_df=.0001,max_df=.3)

    #matrix with each row corresponding to an opinion
    #and each column an n-gram with n specified above
    print(f"Building TF-IDF matrix with {max_n}-grams ...")
    tfidf_matrix =  tf.fit_transform(corpus)
    print("Finished TF-IDF matrix with shape",tfidf_matrix.shape)
    #write sparse tdidf matrix to compressed .npz file
    scipy.sparse.save_npz(TFIDF_MATRIX_PATH, tfidf_matrix)
    print("Saved sparse matrix to ",TFIDF_MATRIX_PATH)

    #mapping {column index : feature name}
    vocab = tf.get_feature_names()
    #mapping {row index : opinion id}
    #opinion_id = U.S. Cite | lower-case-v-name-abbreviated
    vcf_code = list(map(str,opin_df['vcf_code']))
    assert tfidf_matrix.shape[0] == len(vcf_code)
    opin_id = vcf_code
    #store index mappings as CSV
    pd.DataFrame(opin_id).to_csv(TFIDF_ROWS_PATH, encoding='utf-8',index=False)
    print("Saved rows of TF-IDF matrix to ",TFIDF_ROWS_PATH)
    pd.DataFrame(vocab).to_csv(TFIDF_COLS_PATH, encoding='utf-8',index=False)
    print("Saved cols of TF-IDF matrix to ",TFIDF_COLS_PATH)

if __name__ == "__main__":
    tfidf_opins()
