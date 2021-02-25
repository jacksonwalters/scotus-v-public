from flask import Flask, render_template, flash, redirect
from forms import KeywordForm
from load_scotus_data import scotus_tfidf_matrix, scotus_opin_id, scotus_vocab, all_scdb_case_data
from load_public_data import public_tfidf_matrix, public_opin_id, public_vocab, anes_codebook_df
from find_scotus_case import find_scdb_case
from find_public_opinion_question import find_anes_question
from search_scotus_opinions_by_keyword import relevant_cases_scdb_df
from search_public_opinions_by_keyword import relevant_questions_anes_df
from scotus_polarity import sc_polarity
from plot import scotus_plot

#set up Flask app
app = Flask(__name__)
app.secret_key = '@5yHj#bn^&(a62andnf,'

#load scotus data
scotus_vocab = scotus_vocab() #load {col index : vocab} mapping for scotus opinions
scotus_tfidf_matrix = scotus_tfidf_matrix() #load scotus tfidf matrix
scotus_opin_id_df = scotus_opin_id() #load {row index : opinion id} mapping for scotus opinions
all_scdb_case_data=all_scdb_case_data() #get scdb dataframe for all (modern+legacy) cases

#load public data
public_vocab = public_vocab() #load {col index : vocab} mapping
public_tfidf_matrix = public_tfidf_matrix() #load tfidf matrix
public_opin_id = public_opin_id() #load {row index : opinion id} mapping
anes_codebook_df = anes_codebook_df() #load formatted ANES codebook as df

@app.route("/", methods=['GET','POST'])
def search_cases():
    form = KeywordForm()
    if form.validate_on_submit():
        #retrieve keywrods from form
        word1 = form.word1.data.rstrip().lstrip().lower()
        word2 = form.word2.data.rstrip().lstrip().lower()
        word3 = form.word3.data.rstrip().lstrip().lower()
        keywords = [word1,word2,word3]
        #search scotus cases via tf-idf of scotus opinion corpus. returns SCDB sub-df.
        scotus_results = relevant_cases_scdb_df(keywords,scotus_vocab,scotus_tfidf_matrix,scotus_opin_id,all_scdb_case_data)
        #search public opinions via tf-idf of all public opinion questions. returns ANES codebook sub-df
        public_results = relevant_questions_anes_df(keywords,public_vocab,public_tfidf_matrix,public_opin_id,anes_codebook_df)
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
