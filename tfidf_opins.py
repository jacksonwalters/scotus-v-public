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
tf = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df = 0)
tfidf_matrix =  tf.fit_transform(corpus[:3])
