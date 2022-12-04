import mysql.connector
import scipy.sparse

#Create MySQL connection object to database
#sql_password = input("Enter MySQL password: ")
mydb = mysql.connector.connect(
    host = "localhost",
    user = "jackson",
    password = "ColorfulLove19#",
    database = "scvpo"
)

#insert sparse matrix in sql database
scotus_tfidf_sparse_matrix = scipy.sparse.load_npz("./data/tf-idf/scotus_opinion/tfidf_matrix.npz")
rows,cols = scotus_tfidf_sparse_matrix.nonzero()
for row,col in zip(rows,cols):
    mycursor.execute("INSERT INTO scvpo.tfidf_scotus_opinions (row_index,col_index,tfidf_value) \
    VALUES ({row_index},{col_index},{tfidf_value});".format(row_index=row,col_index=col,tfidf_value=scotus_tfidf_sparse_matrix[row,col]))

#print the values in the table tfidf_scotus_opinions
mycursor.execute("SELECT * FROM tfidf_scotus_opinions")
myresult = mycursor.fetchall()
for x in myresult:
  print(x)
