#examples of issues. a set of keywords corresponds to a set of supreme court
#cases and a set of public opinion Q+A's

class Issue:
    def __init__(self, name, keywords, scotus_cases, case_ind, response_map):
        self.name = name
        self.keywords = keywords
        self.scotus_cases = scotus_cases
        self.case_ind = case_ind
        self.response_map = response_map

    def __str__(self):
        return self.name

def civil_rights_issue():
    return Issue(
        name="Civil Rights",
        keywords=['black','color','oppressed','civil','rights'],
        scotus_cases=["Dred Scott v. Sandford (1856)",
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
            "Grutter v. Bollinger (2003)"],
            case_ind=[2488,10220,19387,19575,20272,21112,21562,22828,24116,24444,25009,25736,26502,26966,28853,31724],
            response_map={
                'VCF0216': {i:i-48 for i in range(97)},
                'VCF0517': {1:+1,7:-1},
                'VCF0518': {1:+1,7:-1},
                'VCF0830': {1:+1,7:-1,9:0},
                'VCF0860': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0861': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0862': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0863': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0864': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0865': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0866': {1:-2,2:-1,3:0,4:1,5:2},
                'VCF0867': {1:+1,5:-1},
                'VCF9037': {1:+1,5:-1},
                'VCF9039': {1:+2,2:+1,3:0,4:-1,5:-2},
                'VCF9040': {1:-2,2:-1,3:0,4:+1,5:+2},
                'VCF9041': {1:-2,2:-1,3:0,4:+1,5:+2},
                'VCF9042': {1:2,2:1,3:0,4:-1,5:-2}
            }
        )

#keywords and cases corresponding to gay marriage issue
def gay_marriage_issue():
    return Issue(
        name="Same-Sex Marriage",
        keywords=['gay','lesbian','marriage','same-sex','same sex','homosexual','spouse'],
        scotus_cases=['1985-144','1995-053','2002-083','2012-077','2012-079','2014-070'], #weirdly caseId 1966-119, Loving v. VA is entered twice
        case_ind=[28947,30801,31731,32844,32846,33022],
        response_map={
            'VCF0232': {i: i-48 for i in range(97)}, #polarity unclear as HOT/COLD is hard to judge
            'VCF0877': {1:2,2:1,4:-1,5:-2}, #polarity=descending
            'VCF0878': {1:1,5:-1}, #polarity=descending
            'VCF0876': {1:1,5:-1}, #polarity=descending
            'VCF0876a': {1:2,2:1,4:-1,5:-2}, #polarity=descending
        }
    )

if __name__ == "__main__":
    print(civil_rights_issue(),gay_marriage_issue())
