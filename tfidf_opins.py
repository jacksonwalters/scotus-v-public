import pandas as pd
import numpy as np
import math, os
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse

HOME = "C:\\Users\\jacks\\OneDrive\\GitHub\\scvpo\\" #home path
INPUT_PATH = os.path.join(HOME,'scotus_opinions.csv') #input filename
TFIDF_MATRIX_PATH = os.path.join(HOME,'tfidf_matrix.npz') #tf-idf matrix filepath
TFIDF_ROWS_PATH = os.path.join(HOME,"tfidf_rows.csv") #opin ids filepath
TFIDF_COLS_PATH = os.path.join(HOME,"tfidf_cols.csv") #vocab filepath

#store opinion data as dataframe
opin_df = pd.read_csv(INPUT_PATH)

#generate corpus
corpus=[]
for opin in list(opin_df['opinion']):
    try:
        if math.isnan(opin):
            corpus.append("")
    except TypeError:
        opin_text = str(opin)
        corpus.append(opin_text)

#generate tfidf matrix
max_n=2 #specify maximum n-gram size (length of phrases)
tf = TfidfVectorizer(analyzer='word', ngram_range=(1,max_n), stop_words="english", max_df=.3)

#matrix with each row corresponding to an opinion
#and each column an n-gram with n specified above
tfidf_matrix =  tf.fit_transform(corpus); print(tfidf_matrix.shape)
#write sparse tdidf matrix to compressed .npz file
scipy.sparse.save_npz(TFIDF_MATRIX_PATH, tfidf_matrix)

#mapping {column index : feature name}
vocab = tf.get_feature_names()
#mapping {row index : opinion id}
date = list(map(str,opin_df['date']))
cite = list(map(str,opin_df['citation']))
name = list(map(str,opin_df['case_name']))
opin_id = ["|".join([cite[i],date[i],name[i]]) for i in range(tfidf_matrix.shape[0])]
#store index mappings as CSV
pd.DataFrame(opin_id).to_csv(TFIDF_ROWS_PATH, encoding='utf-8',index=False)
pd.DataFrame(vocab).to_csv(TFIDF_COLS_PATH, encoding='utf-8',index=False)
