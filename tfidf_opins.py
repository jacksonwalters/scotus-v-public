import pandas as pd
import numpy as np
import math
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse

path = '/home/jackson/Documents/scvpo/scotus_opinions.csv'

#store opinion data as dataframe
opin_df = pd.read_csv(path)

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
scipy.sparse.save_npz('/home/jackson/Documents/scvpo/tfidf_matrix.npz', tfidf_matrix)

#mapping {column index : feature name}
vocab = tf.get_feature_names()
#mapping {row index : opinion id}
date = list(map(str,opin_df['date']))
cite = list(map(str,opin_df['citation']))
name = list(map(str,opin_df['case_name']))
opin_id = ["|".join([cite[i],date[i],name[i]]) for i in range(tfidf_matrix.shape[0])]
#store index mappings as CSV
pd.DataFrame(opin_id).to_csv("/home/jackson/Documents/scvpo/tfidf_rows.csv", encoding='utf-8',index=False)
pd.DataFrame(vocab).to_csv("/home/jackson/Documents/scvpo/tfidf_cols.csv", encoding='utf-8',index=False)
