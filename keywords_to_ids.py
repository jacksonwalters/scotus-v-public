import pandas as pd

#FIND RELEVANT CASES BASED ON KEYWORDS
##################################################################

#search for a partial match in
def search(word):
    return all_cd_df[all_cd_df['caseName'].str.contains(word,na=False)]

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
    return {name:sc_find_case(name) for name in CIVIL_RIGHTS_CASES}
