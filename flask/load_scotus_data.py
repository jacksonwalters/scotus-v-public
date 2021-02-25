import scipy.sparse
import pandas as pd

#load scotus tfidf matrix
def scotus_tfidf_matrix():
    return scipy.sparse.load_npz("./data/tf-idf/scotus_opinion/tfidf_matrix.npz")

#load {row index : opinion id} mapping for scotus opinions
def scotus_opin_id():
    scotus_opin_id_df = pd.read_csv("./data/tf-idf/scotus_opinion/tfidf_rows.csv")
    return list(scotus_opin_id_df['0'])

#load {col index : vocab} mapping for scotus opinions
def scotus_vocab():
    scotus_vocab_df = pd.read_csv("./data/tf-idf/scotus_opinion/tfidf_cols.csv")
    return list(scotus_vocab_df['0'])

#get modern scdb case data, 1946 - present
def modern_scdb_case_data():
    return pd.read_csv("./data/scdb/scdb_case_data.csv",encoding='windows-1252')

#path for scotus legacy case data from SCDB, 1789 - 1946
def legacy_scdb_case_data():
    return pd.read_csv('./data/scdb/scdb_legacy_case_data.csv',encoding='windows-1252')

#get scdb dataframe for all (modern+legacy) cases
def all_scdb_case_data():
    return pd.concat([legacy_scdb_case_data(),modern_scdb_case_data()],ignore_index=True)
