import pandas as pd

#given a vcf_code, return the relevant questions from the codebook
def find_anes_question(vcf_code,anes_codebook):
    anes_questions=anes_codebook[anes_codebook['vcf_code']==vcf_code]
    if not anes_questions.empty:
        return anes_questions
    else:
        return pd.DataFrame()
