import re, csv
import pandas as pd

SEP = 99*"="
Q_SEP = "\n\n"
INPUT_PATH = ".\\data\\anes\\codebook\\anes_timeseries_cdf_codebook_var.txt"
OUTPUT_PATH = ".\\data\\anes\\codebook\\formatted_anes_codebook.csv"

def format(question):
        #print(repr(chunk))
        formatted_q = dict({
            "vcf_code":"",
            "code_category":"",
            "question":"",
            "valid_codes":"",
            "missing_codes":"",
            "notes":"",
            "weight":"",
            "source_vars":""
            })

        #split each question by separator Q_SEP = "\n\n"
        question_items = question.split(Q_SEP)
        for item in question_items:
            #VCF code
            codes = [match.strip('\n\t') for match in re.findall("\nVCF\w{4,5}\t",item)]
            if len(codes) >= 1:
                formatted_q["vcf_code"] = codes[0]
            #code category
            if len(question_items) > 1:
                formatted_q["code_category"] = question_items[1]
            #question
            arr = item.split("QUESTION:\n---------\n")
            if len(arr) > 1:
                formatted_q["question"] = arr[1]
            #valid codes
            arr = item.split("VALID CODES:\n------------\n")
            if len(arr) > 1:
                formatted_q["valid_codes"] = arr[1]
            #missing codes
            arr = item.split("MISSING CODES:\n--------------\n")
            if len(arr) > 1:
                formatted_q["missing_codes"] = arr[1]
            #notes
            arr = item.split("NOTES:\n------\n")
            if len(arr) > 1:
                formatted_q["notes"] = arr[1]
            #weight
            arr = item.split("WEIGHT:\n-------\n")
            if len(arr) > 1:
                formatted_q["weight"] = arr[1]
            #source vars
            arr = item.split("SOURCE VARS:\n------------\n")
            if len(arr) > 1:
                formatted_q["source_vars"] = arr[1]

        return formatted_q

if __name__ == "__main__":
    print("Input file: ",INPUT_PATH)
    with open(INPUT_PATH,'r') as f_open:
        data = f_open.read()

    #split questions using SEP = 99*"="
    question_arr = data.split(SEP)
    print("# separators found: ",len(question_arr))

    #for each question, put the data into a dictionary
    formatted_questions=[format(question) for question in question_arr]
    print("# questions found: ",len(formatted_questions))

    f = open(OUTPUT_PATH, "w")
    writer = csv.DictWriter(f, fieldnames=[
            "vcf_code",
            "code_category",
            "question",
            "valid_codes",
            "missing_codes",
            "notes",
            "weight",
            "source_vars"])
    writer.writeheader()
    writer.writerows(formatted_questions)
    f.close()

    print("Output file: ",OUTPUT_PATH)
