"""Exercise raw Stata/CSV -> artifact -> Flask, including failure atomicity."""
import argparse
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from scvpublic.build import build, publish, demo_matrices
from scvpublic.web import create_app


class BuildTests(unittest.TestCase):
    def test_end_to_end_and_newer_release_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'anes/codebook').mkdir(parents=True)
            (root/'scdb').mkdir()
            pd.DataFrame({'vcf_code':['Q1','Q2','Q3','Q4'],
                          'question':['marriage equality','gun control','tax policy','environment protection']}).to_csv(root/'anes/codebook/formatted_anes_codebook.csv',index=False)
            pd.DataFrame({'vcf_code':['Q1'],'ques_class':[1]}).to_csv(root/'anes/classified_questions.csv',index=False)
            answers = pd.DataFrame({'VCF0004':[2000,2000,2016,2016],
                                   'Q1':pd.Categorical(['No','Yes','Yes','Yes'],categories=['No','Yes'])})
            answers.to_stata(root/'anes/input.dta',write_index=False)
            fields=['caseName','usCite','dateDecision','majVotes','minVotes','decisionDirection']
            pd.DataFrame([['EXAMPLE','123 U.S. 456','06/01/2000',6,3,2]],columns=fields).to_csv(root/'scdb/scdb_case_data.csv',index=False)
            pd.DataFrame([],columns=fields).to_csv(root/'scdb/scdb_legacy_case_data.csv',index=False)
            opinions=root/'opinions.csv'
            pd.DataFrame({'citation':['123 U.S. 456','','',''], 'case_name':['example','two','three','four'],
                          'opinion':['marriage equality','gun control','tax policy','environment protection']}).to_csv(opinions,index=False)
            args=argparse.Namespace(data=root,anes=root/'anes/input.dta',opinions=opinions,allow_new_anes=False)
            matrices=build(args)
            output=root/'artifact.sqlite'
            with redirect_stdout(io.StringIO()):
                publish(output,'Test fixture',False,matrices)
            response=create_app(output).test_client().get('/?q1=marriage')
            self.assertEqual(response.status_code,200)
            self.assertIn(b'EXAMPLE',response.data)
            self.assertIn(b'marriage equality',response.data)
            self.assertEqual(matrices[5][0]['years'],{'2000':0.0,'2016':1.0})
            answers['VCF0004']=2024
            answers.to_stata(args.anes,write_index=False)
            with self.assertRaisesRegex(ValueError,'beyond'):
                build(args)
            original=output.read_bytes()
            broken=list(demo_matrices()); broken[1]=['wrong','dimensions']
            with self.assertRaises(ValueError):
                publish(output,'Broken',True,broken)
            self.assertEqual(output.read_bytes(),original)
            self.assertFalse(list(root.glob('.build-*')))
