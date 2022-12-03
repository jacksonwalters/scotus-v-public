import mysql.connector
import scipy.sparse

#scotus_tfidf_sparse_matrix = scipy.sparse.load_npz("./data/tf-idf/scotus_opinion/tfidf_matrix.npz")

# Creating connection object
mydb = mysql.connector.connect(
    host = "localhost",
    user = "example_user",
    password = "ColorfulLove19#",
    database = "example_database"
)

print(mydb)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)

mycursor.execute("SELECT * FROM todo_list")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)
