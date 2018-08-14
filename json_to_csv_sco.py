import csv
import json
import os
from bs4 import BeautifulSoup

#load json files and write to csv file
def json_opins_to_csv():
    data_path = '/Users/jackson/Data/scvpo/scotus_opins_json/'
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
                    #w/ CourtListener data, opin may be stored
                    #in one of three fields: plain text, html, or
                    #possibily html with citation

                    #get plain text. empty string if not present.
                    opin_plain = str(json_data['plain_text'])
                    opin_html = str(json_data['html'])
                    opin_html_cite = str(json_data['html_with_citations'])

                    if opin_html_cite != "":
                        soup = BeautifulSoup(opin_html_cite, 'html.parser')
                        opinion = soup.get_text()
                    elif opin_html != "":
                        soup = BeautifulSoup(opin_html, 'html.parser')
                        opinion = soup.get_text()
                    elif opin_plain != "":
                        opinion = opin_plain

                    #write row to csv file
                    opin_writer.writerow({'case_name': case_name, 'docket': docket, 'opinion': opinion})

                    #print status
                    processed += 1
                    per_complete = 100*round(processed/total_files,4)
                    print(per_complete,"%")
                    continue
            else:
                continue
