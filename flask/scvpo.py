from flask import Flask, render_template, flash, redirect
from forms import KeywordForm
import scipy.sparse
import pandas as pd
import os
from find_scotus_case import find_scdb_case
from scotus_polarity import sc_polarity
from plot import scotus_plot

#set up Flask app
app = Flask(__name__)
app.secret_key = '@5yHj#bn^&(a62andnf,'

#load tfidf matrix
tfidf_matrix = scipy.sparse.load_npz("./data/tfidf_matrix.npz")
#load {row index : opinion id} mapping
opin_id_df = pd.read_csv("./data/tfidf_rows.csv")
opin_id = list(opin_id_df['0'])
#load {col index : vocab} mapping
vocab_df = pd.read_csv("./data/tfidf_cols.csv")
vocab = list(vocab_df['0'])
#get modern scdb case data, 1946 - present
modern_scdb_case_data = pd.read_csv("./data/scdb/scdb_case_data.csv",encoding='windows-1252')
#path for scotus legacy case data from SCDB, 1789 - 1946
legacy_scdb_case_data = pd.read_csv('./data/scdb/scdb_legacy_case_data.csv',encoding='windows-1252')
#get scdb dataframe for all (modern+legacy) cases
all_scdb_case_data=pd.concat([legacy_scdb_case_data,modern_scdb_case_data],ignore_index=True)

#find list of relevant cases given set of keywords
def relevant_cases_by_opin_id(keywords):
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

#given keywords, look up relevant cases by searching opinion text
#match cases to SCDB data and return sub-dataframe
def relevant_cases_scdb_df(keywords):
    opin_ids = relevant_cases_by_opin_id(keywords) #get opinion ids
    scdb_cases = [find_scdb_case(opin_id,all_scdb_case_data) for opin_id in opin_ids] #get list of scdb cases
    #if no scdb_cases is empty list
    if not scdb_cases:
        return pd.DataFrame() #return the empty dataframe
    else:
        return pd.concat(scdb_cases) #concatenate the dataframes and return

@app.route("/", methods=['GET','POST'])
def search_cases():
    form = KeywordForm()
    if form.validate_on_submit():
        #retrieve keywrods from form
        word1 = form.word1.data.rstrip().lstrip().lower()
        word2 = form.word2.data.rstrip().lstrip().lower()
        word3 = form.word3.data.rstrip().lstrip().lower()
        keywords = [word1,word2,word3]
        #search cases via tf-idf and flash output
        results = relevant_cases_scdb_df(keywords)
        if not results.empty:
            #plot {year:polarity} of resulting cases
            plot_filename=scotus_plot(sc_polarity(results),title="+".join(keywords))
            flash(plot_filename,'plot_filename')
            for case_name in results['caseName']:
                flash(case_name,'output')
        else:
            flash("No results!",'output')
        return redirect('/')
    return render_template("index.html",title="SCOTUS v. Public Opinion",form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
