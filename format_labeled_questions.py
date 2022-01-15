import pandas as pd
from load_public_data import anes_codebook

#load classified questions indexed by VCF code
class_ques = pd.read_csv("./data/anes/classified_questions.csv")
#load ANES question data
anes_df = anes_codebook()

#using VCF codes as key, join dataframes and drop unclassified questions
format_ques=anes_df.set_index("vcf_code").join(class_ques.set_index("vcf_code")).dropna()
#clean the question text of newline and tab characters
format_ques["question"] = format_ques["question"].apply(lambda q: ' '.join(q.split()))
#send cleaned results to .txt file, single line, separated by tab character
format_ques[["question","ques_class"]].to_csv('./data/training/labeled_questions.txt', header=None, index=None, sep='\t', mode='a')
