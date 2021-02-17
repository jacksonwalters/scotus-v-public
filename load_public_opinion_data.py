#PUBLIC OPINION DATA
#ANES time series cumulative data. question surveys to monitor voting,
#public opinion, and political participation in the US from 1948-2016.
#55674 rows x 952 columns. ROWS are grouped by YEAR (VCF0004). first few COLS
#represent time and other meta-data, remaining COLS represent responses
#different QUESTIONS.
#roughly 55 million entries

SURVEY_YEAR = 'VCF0004'

PATH = ".\\data\\anes\\"
DATA_TYPES = 'data_types.csv'
PO_DATA = 'anes_data.csv'
DATA_TYPES_PATH = os.join(PATH,DATA_TYPES_PATH)
PO_DATA_PATH = os.join(PATH,PO_DATA)
#identifiers for RELEVANT QUESTIONS from ANES PO surveys
PO_REL_QUES=list(RESP_CONVERT.keys())

def load_po_data():
    #build dict of data types from csv.
    with open(DATA_TYPES_PATH, mode='r') as infile:
        reader = csv.reader(infile)
        data_types = {rows[0]:rows[1] for rows in reader}

    po_df=pd.read_csv(PO_DATA_PATH) #load PO data into dataframe
    rel_po_df = po_df[ [SURVEY_YEAR] + PO_REL_QUES ] #only use relevant public opinion questions

    SURVEY_YEARS=tuple(set(po_df[SURVEY_YEAR]))

if __name__ == "__main__":
