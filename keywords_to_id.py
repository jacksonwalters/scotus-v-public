import pandas as pd

#search for a partial match in
def search(word):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

#BLACK RIGHTS
######################################################################

#case names
civil_rights_cases=["Dred Scott v. Sanford (1856)",
"Plessy v. Ferguson (1896)",
"Korematsu v. U.S. (1944)",
"Shelley v. Kraemer (1948)",
"Brown v. Board of Education (1954)",
"Brown v. Board of Education II (1955)",
"Bailey v. Patterson (1962)",
"Loving v. Virginia (1967)",
"Jones v. Mayer Co. (1968)",
"Griggs v. Duke Power Co. (1971)",
"Lau v. Nichols (1974)",
"Village of Arlington Heights v. Metropolitan Housing Development Corp. (1977)",
"University of California Regents v. Bakke (1978)",
"Batson v. Kentucky (1986)",
"Grutter v. Bollinger (2003)"
]

#case_ids
civil_rights_ids=[2488,10220,]

#possible ids
[set(),
{10220},
set(),
{411, 412},
{1251, 1252, 1701, 1253, 5198, 4529, 1268, 1560},
set(),
{2996, 2997, 2998, 2967},
{4256, 4255},
{4584, 4585, 4583},
{5148}, {5875},
{6641, 6642},
set(),
{8992, 8993},
{11864, 11865, 11863}]

def sc_find_case(name):
    upper=str.upper(name)
    words=upper.split()
    key_words=[]
    year=int(words.pop().strip("()"))
    words=" ".join(words).split("V.")
    party1=words[0].strip()
    party2=words[1].strip()
    df1=search(party1)
    index1=set(list(df1.index))
    df2=search(party2)
    index2=set(list(df2.index))
    #pd.merge(df1,df2,how="inner")
    return index1.intersection(index2)

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
