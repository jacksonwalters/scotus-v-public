import csv
import json
import os
import pandas as pd
from bs4 import BeautifulSoup

#load json files and write to csv file
def json_opins_to_csv():
    data_path = '/Users/jackson/Data/scvpo/scotus_opins_json/'
    data_dict = {'citation': [],'case_name': [],'date': [], 'opinion': []}

    #each json file contributes a row to the big csv file
    processed = 0
    total_files = 63991
    for file in os.listdir(data_path):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            with open(os.path.join(data_path, filename)) as opinion_json:
                #load data from json
                json_data = json.load(opinion_json)

                #try getting CITATION, from download_url
                dl_url = str(json_data['download_url'])
                citation = dl_url.split('/')[-1]

                #try getting CASE NAME, from absolute_url
                abs_url = str(json_data['absolute_url'])
                case_name = abs_url.split('/')[-2]

                #get date
                date = ""

                #retrieve opinion text
                #w/ CourtListener data, opin may be stored
                #in a number of fields:
                #plain_text
                #html
                #html_with_citations

                #GET BEST OPINION TEXT POSSIBLE
                #TRY TO EXTRACT DATE, CITATION, NAME from HTML
                opin_plain = str(json_data['plain_text'])
                opin_html = str(json_data['html'])
                opin_html_cite = str(json_data['html_with_citations'])

                if opin_html_cite != "":
                    soup = BeautifulSoup(opin_html_cite, 'html.parser')
                    opin_text = soup.get_text()
                    opin_text = opin_text.split('\n')
                    opinion = ' '.join(opin_text)
                elif opin_html != "":
                    soup = BeautifulSoup(opin_html, 'html.parser')
                    opin_text = soup.get_text()
                    opin_text = opin_text.split('\n')
                    opinion = ' '.join(opin_text)
                elif opin_plain != "":
                    opin_text = opin_plain
                    opin_text = opin_text.split('\n')
                    opinion = ' '.join(opin_text)

                #write row to csv file
                data_dict['citation'].append(citation)
                data_dict['case_name'].append(case_name)
                data_dict['date'].append(date)
                data_dict['opinion'].append(opinion)

                #print status
                if opinion != "":
                    processed += 1
                per_complete = 100*round(processed/total_files,4)
                print(per_complete,"%")

                #for testing
                if processed == 5:
                    break
                else:
                    continue
        else:
            continue

    #store data dictionary in pandas df
    opin_df = pd.DataFrame.from_dict(data=data_dict)

    #write dataframe to file
    out_path = "/Users/jackson/Data/scvpo/"
    out_name = "scotus_opinions.csv"
    full_name = os.path.join(out_path,out_name)
    opin_df.to_csv(full_name, encoding='utf-8')
