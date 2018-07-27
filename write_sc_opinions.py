import csv
import json

#load json files and write to csv file
def load_json_opinions():
    data_path = '/Users/jackson/Data/scvpo/scotus_opinions_test/'
    with open('sc_opinions.csv', 'w',newline='') as csvfile:
        fieldnames = ['scdb_id', 'opinion']
        opin_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        opin_writer.writeheader()
        #each json file contributes a row to the big csv file
        for file in os.listdir(data_path):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                with open(os.path.join(data_path, filename)) as opinion_json:
                    data = json.load(opinion_json)
                    opinion_text = data['plain_text']
                    opin_writer.writerow({'scdb_id': 1234, 'opinion': opinion_text})
                    continue
            else:
                continue