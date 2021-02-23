import pandas as pd

CODEBOOK_PATH = "anes/codebook/formatted_anes_codebook.csv"
DATA_PATH = "anes/anes_timeseries_cdf.dta"

if __name__ == "__main__":
    codebook_df=pd.read_csv(CODEBOOK_PATH)
    anes_df=pd.read_stata(DATA_PATH)
    print(list(codebook_df["vcf_code"])[:10])
    print(list(anes_df)[:10])
