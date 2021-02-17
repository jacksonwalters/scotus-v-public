from flask import Flask, render_template, flash, redirect
from forms import KeywordForm
import scipy.sparse
import pandas as pd

#set up Flask app
app = Flask(__name__)
app.secret_key = 'secret_key'

#load tfidf matrix
tfidf_matrix = scipy.sparse.load_npz("./data/tfidf_matrix.npz")
#load {row index : opinion id} mapping
opin_id_df = pd.read_csv("./data/tfidf_rows.csv")
opin_id = list(opin_id_df['0'])
#load {col index : vocab} mapping
vocab_df = pd.read_csv("./data/tfidf_cols.csv")
vocab = list(vocab_df['0'])

#find list of relevant cases given set of keywords
def relevant_cases(keywords):
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

@app.route("/", methods=['GET','POST'])
def search_cases():
    form = KeywordForm()
    if form.validate_on_submit():
        #retrieve keywrods from form
        word1 = form.word1.data.strip().lower()
        word2 = form.word2.data.strip().lower()
        word3 = form.word3.data.strip().lower()
        keywords = [word1,word2,word3]
        #search cases via tf-idf and flash output
        results = relevant_cases(keywords)
        for case in results:
            flash(case,'output')
        return redirect('/')
    return render_template("index.html",title="SCOTUS v. Public Opinion",form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
