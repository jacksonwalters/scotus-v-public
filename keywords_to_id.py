import pandas as pd

#search for a partial match in
def search(word):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

#BLACK RIGHTS
######################################################################

#natural language case names
civil_rights_cases=["Dred Scott v. Sandford (1856)",
"Plessy v. Ferguson (1896)",
"Korematsu v. UNITED STATES (1942)",
"Korematsu v. UNITED STATES (1944)",
"Shelley v. Kraemer (1948)", #split vote
"Brown v. Board of Education (1954)",
"Brown v. Board of Education (1955)",
"Bailey v. Patterson (1962)",
"Loving v. Virginia (1967)",
"Jones v. Mayer Co. (1968)",
"Griggs v. Duke Power Co. (1971)",
"Lau v. Nichols (1974)",
"Village of Arlington Heights v. Metropolitan Housing Development Corp. (1977)",
"Regents of the University of California v. Bakke (1978)",
"Batson v. Kentucky (1986)",
"Grutter v. Bollinger (2003)"
]

#POSSIBLE MATCHES
#nb: some repeat IDs due to unique voteId column
#nb: U.S. <-> UNITED STATES
#check for misspellings
#check year to avoid repeats
poss_match={
'Dred Scott v. Sandford (1856)': ['1856-061'],
'Plessy v. Ferguson (1896)': ['1895-271'],
'Korematsu v. UNITED STATES (1942)': ['1942-142', '1944-018'],
'Korematsu v. UNITED STATES (1944)': ['1942-142', '1944-018'],
'Shelley v. Kraemer (1948)': ['1947-072'],
'Brown v. Board of Education (1954)': ['1952-001', '1952-015', '1953-069', '1954-085'],
'Brown v. Board of Education (1955)': ['1952-001', '1952-015', '1953-069', '1954-085'],
'Bailey v. Patterson (1962)': ['1961-019', '1961-039'],
'Loving v. Virginia (1967)': ['1966-119'],
'Jones v. Mayer Co. (1968)': ['1967-181'],
'Griggs v. Duke Power Co. (1971)': ['1970-056'],
'Lau v. Nichols (1974)': ['1973-041'],
'Village of Arlington Heights v. Metropolitan Housing Development Corp. (1977)': ['1976-028'],
'Regents of the University of California v. Bakke (1978)': ['1977-147'],
'Batson v. Kentucky (1986)': ['1985-078'],
'Grutter v. Bollinger (2003)': ['2002-078']
}

#CASE IDS
civil_rights_ids=[2488,
10220,
19387,
19575,
411,#412,
1560, 1701,
2996, #2997, 2998
4255, #4256
4583, #4584, 4585
5148,
5875,
6641, #6642,
7105, #7106, 7107
8992, #8993,
11863, #11864, 11865
]

def sc_find_case(name):
    upper=str.upper(name)
    words=upper.split()
    key_words=[]
    year=int(words.pop().strip("()"))
    words=" ".join(words).split("V.")

    #should search for all words in each party name
    party1=words[0].strip()
    party2=words[1].strip()

    df1=search(party1)
    index1=set(list(df1.caseId))

    df2=search(party2)
    index2=set(list(df2.caseId))

    result = sorted(list(index1.intersection(index2)))

    return result

def possible_matches():
    return {name:sc_find_case(name) for name in civil_rights_cases}



#GAY MARRIAGE
######################################################################

#identifiers for RELEVANT CASES from SCDB
#KEY Q: HOW TO GET RELEVANT CASES FROM KEYWORDS
#A: scrape opinion text from web or load into db. classify utilizing keywords and tfidf.
gay_marriage_rel_ids=['1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'] #weirdly caseId 1966-119, Loving v. VA is entered twice
#N.B.: case indices are unique, but only for *case* centered data.
gay_marriage_rel_ind=[9086,10940,11870,12983,12985,13161]
