import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

path = '/Users/jackson/Data/scvpo/sc_opinions.csv'

#store opinion data as dataframe
opin_df = pd.read_csv(path)

#generate corpus
corpus=list(opin_df['opinion'])

#generate tfidf matrix
tf = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df = 0)
