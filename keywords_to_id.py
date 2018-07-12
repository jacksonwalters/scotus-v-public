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
#don't use indices - merging dfs will mess with this!
poss_match={'Dred Scott v. Sandford (1856)': [2488],
'Plessy v. Ferguson (1896)': [10220],
'Korematsu v. UNITED STATES (1942)': [19387, 19575],
'Korematsu v. UNITED STATES (1944)': [19387, 19575],
'Shelley v. Kraemer (1948)': [20272, 20273],
'Brown v. Board of Education (1954)': [21112, 21113, 21114, 21129, 21421, 21562],
'Brown v. Board of Education (1955)': [21112, 21113, 21114, 21129, 21421, 21562],
'Bailey v. Patterson (1962)': [22828, 22857, 22858, 22859],
'Loving v. Virginia (1967)': [24116, 24117],
'Jones v. Mayer Co. (1968)': [24444, 24445, 24446],
'Griggs v. Duke Power Co. (1971)': [25009],
'Lau v. Nichols (1974)': [25736],
'Village of Arlington Heights v. Metropolitan Housing Development Corp. (1977)': [26502, 26503],
'Regents of the University of California v. Bakke (1978)': [26966, 26967, 26968],
'Batson v. Kentucky (1986)': [28853, 28854],
'Grutter v. Bollinger (2003)': [31724, 31725, 31726]}

#CASE IDS
civil_rights_ids=[2488,
10220,
19387,
19575,
20272,
21112,
21562,
22828,
24116,
24444,
25009,
25736,
26502,
26966,
28853,
31724
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
    index1=set(list(df1.index))

    df2=search(party2)
    index2=set(list(df2.index))

    result = sorted(list(index1.intersection(index2)))

    return result

def possible_ids():
    return {name:sc_find_case(name) for name in civil_rights_cases}

#GAY MARRIAGE
######################################################################

#identifiers for RELEVANT CASES from SCDB
#KEY Q: HOW TO GET RELEVANT CASES FROM KEYWORDS
#A: scrape opinion text from web or load into db. classify utilizing keywords and tfidf.
gay_marriage_rel_ids=['1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'] #weirdly caseId 1966-119, Loving v. VA is entered twice
#N.B.: case indices are unique, but only for *case* centered data.
gay_marriage_rel_ind=[9086,10940,11870,12983,12985,13161]
