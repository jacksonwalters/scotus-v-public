import mysql.connector
import scipy.sparse

#Create MySQL connection object to database
#sql_password = input("Enter MySQL password: ")
mydb = mysql.connector.connect(
    host = "localhost",
    user = "jackson",
    password = "your-password-here",
    database = "scvpo"
)
mycursor = mydb.cursor()

mycursor.execute("SELECT row_index FROM scvpo.tfidf_scotus_opinions ORDER BY row_index DESC LIMIT 1;")
myresult = mycursor.fetchall()
print(myresult[0][0])

mycursor.execute("SELECT tfidf_value FROM scvpo.tfidf_scotus_opinions WHERE row_index=0 AND col_index=12313213;")
myresult = mycursor.fetchall()
print(len(myresult))
for x in myresult:
  print(x[0])

#insert sparse matrix in sql database
scotus_tfidf_sparse_matrix = scipy.sparse.load_npz("./data/tf-idf/scotus_opinion/tfidf_matrix.npz")
rows,cols = scotus_tfidf_sparse_matrix.nonzero()
assert len(rows) == len(cols)
BATCH_NUM = 22
BATCH_SIZE = 1_000_000
START = BATCH_NUM*BATCH_SIZE
END = (BATCH_NUM+1)*BATCH_SIZE
count = 0
for row,col in zip(rows[START:END],cols[START:END]):
    if count%1_000 == 0: print(count/BATCH_SIZE)
    mycursor.execute("INSERT INTO scvpo.tfidf_scotus_opinions (row_index,col_index,tfidf_value) \
    VALUES ({row_index},{col_index},{tfidf_value});".format(row_index=row,col_index=col,tfidf_value=scotus_tfidf_sparse_matrix[row,col]))
    count+=1

mydb.commit()
mycursor.close()
mydb.close()
