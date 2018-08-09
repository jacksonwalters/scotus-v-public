import csv
import json

#load json files and write to csv file
def json_opins_to_csv():
    data_path = '/Users/jackson/Data/scvpo/scotus_opinions/'
    with open('sc_opinions.csv', 'w',newline='') as csvfile:
        fieldnames = ['case_name','docket','opinion']
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
                    json_data = json.load(opinion_json)

                    #get docket from end of download url
                    #may be null
                    dl_url = str(json_data['download_url'])
                    docket = dl_url.split('/')[-1]

                    #get case name from end of absolute url
                    #not a unique identifier
                    abs_url = str(json_data['absolute_url'])
                    case_name = abs_url.split('/')[-2]

                    #retrieve opinion text
                    opinion_text = str(json_data['plain_text'])

                    #write row to csv file
                    opin_writer.writerow({'case_name': case_name, 'docket': docket, 'opinion': opinion_text})

                    #print status
                    processed += 1
                    per_complete = 100*round(processed/total_files,4)
                    print(per_complete,"%")
                    continue
            else:
                continue
