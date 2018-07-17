#scrape supreme court opinions from CourtListener at
#https://www.courtlistener.com/c/
#US Court Citation -> /c/U.S./410/113/ = /c/U.S./volume/page
#Supreme Court Citation -> /c/S. Ct./410/113/ = /c/S. Ct./volume/page

import requests
import math
import sys
from bs4 import BeautifulSoup

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
def get_opinion_text(ind,id=None):
    response = requests.get(BASE_URL + get_citation_url(ind))
    soup = BeautifulSoup(response.text)
    opinion_content = soup.select('div#opinion-content') #returns a list
    opinion_text = str(opinion_content)
    return opinion_text
