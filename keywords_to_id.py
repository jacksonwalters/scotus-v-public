#search for a partial match in
def sc_search(word,col_name,df):
    df[df[col_name].str.contains(word,na=False)]

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

#GAY MARRIAGE
######################################################################

#identifiers for RELEVANT CASES from SCDB
#KEY Q: HOW TO GET RELEVANT CASES FROM KEYWORDS
#A: scrape opinion text from web or load into db. classify utilizing keywords and tfidf.
gay_marriage_rel_ids=['1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'] #weirdly caseId 1966-119, Loving v. VA is entered twice
#N.B.: case indices are unique, but only for *case* centered data.
gay_marriage_rel_ind=[9086,10940,11870,12983,12985,13161]
