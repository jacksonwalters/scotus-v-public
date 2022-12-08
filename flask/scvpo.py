from flask import Flask, render_template, flash, redirect
from forms import KeywordForm
from load_scotus_data import scotus_tfidf_matrix, scotus_opin_id, scotus_vocab, all_scdb_case_data
from load_public_data import public_tfidf_matrix, public_opin_id, public_vocab, anes_codebook_df, anes_opinion_data
from search_scotus_opinions_by_keyword import relevant_cases_scdb_df
from search_public_opinions_by_keyword import relevant_questions_anes_df
from polarity_scotus import sc_polarity
from polarity_public import po_polarity
from plot import scotus_v_public_plot
#import mysql.connector

#set up Flask app
app = Flask(__name__)
app.secret_key = '@5yHj#bn^&(a62andnf,'
SURVEY_YEAR_VCF_CODE = 'VCF0004' #ANES code for survey year

#Create MySQL connection object to database
#sql_password = input("Enter MySQL password: ")
"""
mydb = mysql.connector.connect(
    host = "localhost",
    user = "jackson",
    password = "ColorfulLove19#",
    database = "scvpo"
)
scotus_tfidf_db_cursor = mydb.cursor()
"""

#load scotus data
scotus_vocab = scotus_vocab() #load {col index : vocab} mapping for scotus opinions
scotus_tfidf_matrix_sparse = scotus_tfidf_matrix() #load scotus tfidf matrix
scotus_opin_id_df = scotus_opin_id() #load {row index : opinion id} mapping for scotus opinions
all_scdb_case_data=all_scdb_case_data() #get scdb dataframe for all (modern+legacy) cases

#load public data
public_vocab = public_vocab() #load {col index : vocab} mapping
public_tfidf_matrix_sparse = public_tfidf_matrix() #load tfidf matrix
public_opin_id_df = public_opin_id() #load {row index : opinion id} mapping
anes_codebook_df = anes_codebook_df() #load formatted ANES codebook as df
anes_response_df = anes_opinion_data() #load the full ANES response data

@app.route("/", methods=['GET','POST'])
def scotus_v_public():
    form = KeywordForm()
    if form.validate_on_submit():
        #retrieve keywrods from form
        word1 = form.word1.data.rstrip().lstrip().lower()
        word2 = form.word2.data.rstrip().lstrip().lower()
        word3 = form.word3.data.rstrip().lstrip().lower()
        keywords = [word1,word2,word3]
        #search scotus cases via tf-idf of scotus opinion corpus. returns SCDB sub-df.
        scotus_results = relevant_cases_scdb_df(keywords,scotus_vocab,scotus_tfidf_matrix_sparse,scotus_opin_id_df,all_scdb_case_data)
        scotus_polarity = None
        #search public opinions via tf-idf of all public opinion questions. returns ANES codebook sub-df
        public_results = relevant_questions_anes_df(keywords,public_vocab,public_tfidf_matrix_sparse,public_opin_id_df,anes_codebook_df)
        public_polarity = None
        #if results for public opinion, flash questions and compute public opinion polarity
        if not public_results.empty:
            for case_name in public_results['question']:
                flash(case_name,'public_output')
            rel_vcf_codes = [SURVEY_YEAR_VCF_CODE]+list(public_results['vcf_code']) #get relevant vcf codes including code for survey year
            rel_ans_df = anes_response_df.filter(items=rel_vcf_codes) #filter the relevant repsonses/answers by VCF code
            public_polarity = po_polarity(public_results,rel_ans_df) #compute polarity of public opinion
        else:
            flash("No relevant questions!",'public_output')
        #if only results for scotus cases, flash cases and plot scotus polarity
        if not scotus_results.empty:
            for case_name in scotus_results['caseName']:
                flash(case_name,'scotus_output')
            scotus_polarity = sc_polarity(scotus_results) #compute polarity of scotus opinions
        else:
            flash("No relevant cases!",'scotus_output')
        #plot with results available. no results ==> empty, neutral plot.
        plot_filename=scotus_v_public_plot(sc_polarity=scotus_polarity,po_polarity=public_polarity,title="+".join(keywords))
        flash(plot_filename,'plot_filename')
        return redirect('/')
    return render_template("index.html",title="SCOTUS v. Public Opinion",form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
