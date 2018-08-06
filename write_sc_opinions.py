import csv
import json

#load json files and write to csv file
def json_opins_to_csv():
    data_path = '/Users/jackson/Data/scvpo/scotus_opinions/'
    with open('sc_opinions.csv', 'w',newline='') as csvfile:
        fieldnames = ['id', 'opinion']
        opin_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        opin_writer.writeheader()

        #each json file contributes a row to the big csv file
        total_files = 63991
        processed = 0
        for file in os.listdir(data_path):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                with open(os.path.join(data_path, filename)) as opinion_json:
                    data = json.load(opinion_json)
                    id = filename.strip(".json")
                    opinion_text = data['plain_text']
                    opin_writer.writerow({'id': id, 'opinion': opinion_text})
                    processed += 1
                    print(round(processed/total_files,2))
                    continue
            else:
                continue
