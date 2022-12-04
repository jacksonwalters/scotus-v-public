import mysql.connector
import scipy.sparse

#scotus_tfidf_sparse_matrix = scipy.sparse.load_npz("./data/tf-idf/scotus_opinion/tfidf_matrix.npz")

#sql_password = input("Enter MySQL password: ")

# Creating connection object
mydb = mysql.connector.connect(
    host = "localhost",
    user = "jackson",
    password = ColorfulLove19#,
    database = "scvpo"
)

print(mydb)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)

mycursor.execute("SELECT * FROM tfidf_scotus_opinions")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)
