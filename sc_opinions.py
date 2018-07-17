#scrape supreme court opinions from CourtListener at
#https://www.courtlistener.com/c/
#US Court Citation -> /c/U.S./410/113/ = /c/U.S./volume/page
#Supreme Court Citation -> /c/S. Ct./410/113/ = /c/S. Ct./volume/page

import requests
import math
import sys
import csv
from bs4 import BeautifulSoup

sys.path.insert(0, '/Users/jackson/Documents/GitHub/requests-futures')
from requests_futures.sessions import FuturesSession

BASE_URL = 'https://www.courtlistener.com/c/'

def get_citation_url(ind,id=None):
    if id != None:
        us_citation = str(all_cd_df.loc[cd_df['caseId'] == id]['usCite'])
        sc_citation = str(all_cd_df.loc[cd_df['caseId'] == id]['sctCite'])
    else:
        us_citation = str(all_cd_df.iloc[ind]['usCite'])
        sc_citation = str(all_cd_df.iloc[ind]['sctCite'])
    if us_citation != 'nan':
        citation = us_citation.split()
        reporter = 'U.S.'
        volume = str(citation[0])
        page = str(citation[2])
    elif sc_citation != 'nan':
        citation= sc_citation.split()
        reporter = 'S. Ct.'
        volume = str(citation[0])
        page = str(citation[3])
    else:
        return float('NaN')

    citation_url = '/'.join([reporter,volume,page])
    return citation_url

#get opinion text given supreme court case id
#relevant tag is 'opinion content'
def opinion_text(response):
    soup = BeautifulSoup(response.text)
    opinion_content = soup.select('div#opinion-content') #returns a list
    if len(opinion_content) == 0:
        return ""
    else:
        return str(opinion_content)

#put all opinion text into database
def scrape_opinions():
    num_cases = len(all_cd_df)
    session = FuturesSession(max_workers=3)
    #create all requests in parallel
    futures = {ind:session.get(BASE_URL + get_citation_url(ind)) for ind in range(10)}
    #collect all results
    responses = {ind:futures[ind].result() for ind in range(10)}
    return responses

def write_opinion_db(result):
    #write all responses of requests to .csv file
    with open('sc_opinions.csv', 'w') as csvfile:
        opinion_writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for ind, response in responses.items():
            opinion_writer.writerow([ind,opinion_text(response)])
