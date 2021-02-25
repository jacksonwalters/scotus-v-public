from flask import Flask, render_template, flash, redirect
from forms import KeywordForm
import scipy.sparse
import pandas as pd
import os
from find_scotus_case import find_scdb_case
from find_public_opinion_question import find_anes_question
from scotus_polarity import sc_polarity
from plot import scotus_plot
from load_scotus_data import scotus_tfidf_matrix

#set up Flask app
app = Flask(__name__)
app.secret_key = '@5yHj#bn^&(a62andnf,'

#load scotus tfidf matrix
scotus_tfidf_matrix = scotus_tfidf_matrix()
#load {row index : opinion id} mapping for scotus opinions
scotus_opin_id_df = pd.read_csv("./data/tf-idf/scotus_opinion/tfidf_rows.csv")
scotus_opin_id = list(scotus_opin_id_df['0'])
#load {col index : vocab} mapping for scotus opinions
scotus_vocab_df = pd.read_csv("./data/tf-idf/scotus_opinion/tfidf_cols.csv")
scotus_vocab = list(scotus_vocab_df['0'])
#get modern scdb case data, 1946 - present
modern_scdb_case_data = pd.read_csv("./data/scdb/scdb_case_data.csv",encoding='windows-1252')
#path for scotus legacy case data from SCDB, 1789 - 1946
legacy_scdb_case_data = pd.read_csv('./data/scdb/scdb_legacy_case_data.csv',encoding='windows-1252')
#get scdb dataframe for all (modern+legacy) cases
all_scdb_case_data=pd.concat([legacy_scdb_case_data,modern_scdb_case_data],ignore_index=True)

#load formatted ANES codebook as df
anes_codebook_df = pd.read_csv("./data/anes/formatted_anes_codebook.csv")
#load tfidf matrix
public_tfidf_matrix = scipy.sparse.load_npz("./data/tf-idf/public_opinion/tfidf_matrix.npz")
#load {row index : opinion id} mapping
public_opin_id_df = pd.read_csv("./data/tf-idf/public_opinion/tfidf_rows.csv")
public_opin_id = list(public_opin_id_df['0'])
#load {col index : vocab} mapping
public_vocab_df = pd.read_csv("./data/tf-idf/public_opinion/tfidf_cols.csv")
public_vocab = list(public_vocab_df['0'])

#find list of relevant cases given set of keywords
def relevant_cases_by_opin_id(keywords):
    keyword_ind = [scotus_vocab.index(keyword) for keyword in keywords if keyword in scotus_vocab]

    #score each opinion (row) based on keywords appearing
    #by summing tfidf scores in the relevant columns
    num_opinions = scotus_tfidf_matrix.shape[0]
    scores = []
    for row in range(num_opinions):
        score = sum(scotus_tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value, in descending order
    scores.sort(key=lambda tup: tup[1],reverse=True)

    #get relevant cases
    rel_cases = [scotus_opin_id[case[0]] for case in scores[:10]]

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

#find list of relevant cases given set of keywords
#returns list of vcf codes for public opinion
def relevant_questions_by_vcf_code(keywords):
    keyword_ind = [public_vocab.index(keyword) for keyword in keywords if keyword in public_vocab]

    #score each opinion (row) based on keywords appearing
    #by summing tfidf scores in the relevant columns
    num_questions = public_tfidf_matrix.shape[0]
    scores = []
    for row in range(num_questions):
        score = sum(public_tfidf_matrix[row,ind] for ind in keyword_ind)
        if score != 0:
            scores.append( (row,score) )

    #sort scores by score value, in descending order
    scores.sort(key=lambda tup: tup[1],reverse=True)

    #get relevant questions
    rel_questions = [public_opin_id[case[0]] for case in scores[:10]]

    return rel_questions

#given keywords, look up relevant questions by searching question text
#and return ANES codebook sub-dataframe
def relevant_questions_anes_df(keywords):
    vcf_codes = relevant_questions_by_vcf_code(keywords) #get public opinion vcf codes
    rel_questions = [find_anes_question(vcf_code,anes_codebook_df) for vcf_code in vcf_codes] #get list of public opinion questions
    #if there are no relevant questions, return the empty dataframe
    if not rel_questions:
        return pd.DataFrame()
    else:
        return pd.concat(rel_questions) #concatenate into single df and return

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
        scotus_results = relevant_cases_scdb_df(keywords)
        public_results = relevant_questions_anes_df(keywords)
        if not scotus_results.empty:
            #plot {year:polarity} of resulting cases
            plot_filename=scotus_plot(sc_polarity(scotus_results),title="+".join(keywords))
            flash(plot_filename,'plot_filename')
            for case_name in scotus_results['caseName']:
                flash(case_name,'output')
        else:
            flash("No results!",'output')
        return redirect('/')
    return render_template("index.html",title="SCOTUS v. Public Opinion",form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
