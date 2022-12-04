import mysql.connector
import scipy.sparse

scotus_tfidf_sparse_matrix = scipy.sparse.load_npz("./data/tf-idf/scotus_opinion/tfidf_matrix.npz")

#sql_password = input("Enter MySQL password: ")

# Creating connection object
mydb = mysql.connector.connect(
    host = "localhost",
    user = "jackson",
    password = "ColorfulLove19#",
    database = "scvpo"
)

mycursor = mydb.cursor()
mycursor.execute("SHOW DATABASES")
for x in mycursor:
  print(x)

num_rows = scotus_tfidf_sparse_matrix.shape[0]
num_cols = scotus_tfidf_sparse_matrix.shape[1]

mycursor.execute("INSERT INTO scvpo.tfidf_scotus_opinions (row_index,col_index,tfidf_value) \
                VALUES ({row_index},{col_index},{tfidf_value});".format(row_index=0,col_index=0,tfidf_value=0.0))

#print the values in the table tfidf_scotus_opinions
mycursor.execute("SELECT * FROM tfidf_scotus_opinions")
myresult = mycursor.fetchall()
for x in myresult:
  print(x)
