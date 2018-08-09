import pandas as pd
import numpy as np
import math
from sklearn.feature_extraction.text import TfidfVectorizer

path = '/Users/jackson/Data/scvpo/sc_opinions.csv'

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
max_n=1 #specify maximum n-gram size (length of phrases)
tf = TfidfVectorizer(analyzer='word', ngram_range=(1,max_n), min_df = 0)

#matrix with each row corresponding to an opinion
#and each column an n-gram with n specified above
tfidf_matrix =  tf.fit_transform(corpus)
print(tfidf_matrix.shape)

#should write this to CSV file

#extract feature names, i.e. column heads
feature_names = tf.get_feature_names()
print(feature_names[:5])
