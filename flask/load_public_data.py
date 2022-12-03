import scipy.sparse
import pandas as pd

#load formatted ANES codebook as df
def anes_codebook_df():
    return pd.read_csv("./data/anes/formatted_anes_codebook.csv")

#load tfidf matrix
def public_tfidf_matrix():
    return scipy.sparse.load_npz("./data/tf-idf/public_opinion/tfidf_matrix.npz")

#load {row index : opinion id} mapping
def public_opin_id():
    public_opin_id_df = pd.read_csv("./data/tf-idf/public_opinion/tfidf_rows.csv")
    return list(public_opin_id_df['0'])

#load {col index : vocab} mapping
def public_vocab():
    public_vocab_df = pd.read_csv("./data/tf-idf/public_opinion/tfidf_cols.csv")
    return list(public_vocab_df['0'])

#load full ANES public opinion responses
def anes_opinion_data():
    return pd.read_stata("./data/anes/anes_timeseries_cdf.dta")

#load list of {-1,0,+1} classified questions as df
def classified_questions():
    return pd.read_csv("./data/anes/classified_questions.csv",index_col='vcf_code')
