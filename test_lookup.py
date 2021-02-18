from load_scotus_data import all_scdb_case_data
from load_scotus_data import scotus_opinion_data
from find_scotus_case import find_scdb_case
import sys

if __name__ == "__main__":
    opin_data=scotus_opinion_data()
    scdb_data=all_scdb_case_data()
    index = int(sys.argv[1])
    citation=opin_data['citation'].iloc[index]
    case_name=opin_data['case_name'].iloc[index]
    opin_id='|'.join([citation,case_name])
    print(opin_id)
    print(find_scdb_case(opin_id,scdb_data))
