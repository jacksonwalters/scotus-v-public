import csv
import json

#load json files and write to csv file
def json_opins_to_csv():
    data_path = '/Users/jackson/Data/scvpo/scotus_opinions/'
    with open('sc_opinions.csv', 'w',newline='') as csvfile:
        fieldnames = ['id','case_name','docket','opinion']
        opin_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        opin_writer.writeheader()

        #each json file contributes a row to the big csv file
        processed = 0
        total_files = 63991
        for file in os.listdir(data_path):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                with open(os.path.join(data_path, filename)) as opinion_json:
                    #load data from json
                    data = json.load(opinion_json)

                    #get relevant data
                    id = filename.strip(".json")
                    opinion_text = str(data['plain_text'])
                    dl_url = str(data['download_url'])
                    docket = dl_url.split('/')[-1]
                    abs_url = str(data['absolute_url'])
                    case_name = abs_url.split('/')[-1]

                    #write row to csv file
                    opin_writer.writerow({'id': id, 'case_name': case_name, 'docket': docket, 'opinion': opinion_text})

                    #print status
                    processed += 1
                    per_complete = 100*round(processed/total_files,4)
                    print(per_complete,"%")
                    continue
            else:
                continue
