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
mycursor = mydb.cursor()

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
