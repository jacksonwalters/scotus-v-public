from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit
import pandas as pd
from scvpublic.courtlistener import initial_url, open_cache, set_scope, save_page, export
from scvpublic.sample import build_sample
from scvpublic.web import create_app


class SampleTests(unittest.TestCase):
    def test_date_filter_and_scope_protection(self):
        query=parse_qs(urlsplit(initial_url('opinions','2015-06-22','2015-06-26')).query)
        self.assertEqual(query['cluster__date_filed__gte'],['2015-06-22'])
        with tempfile.TemporaryDirectory() as temp:
            db=open_cache(Path(temp)/'cache.sqlite')
            try:
                set_scope(db,'2015-06-22','2015-06-26')
                with self.assertRaisesRegex(ValueError,'differs'):
                    set_scope(db,None,None)
            finally:
                db.close()

    def test_partial_sample_is_not_complete_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); db=open_cache(root/'cache.sqlite')
            try:
                cluster=dict(id=1,case_name='Sample',citations=[],date_filed='2015-06-22')
                opinion=dict(id=2,cluster=1,plain_text='Sample text')
                for kind,row in [('clusters',cluster),('opinions',opinion)]:
                    save_page(db,kind,initial_url(kind),json.dumps(dict(results=[row],next=initial_url(kind)+'&cursor=next')).encode())
                with self.assertRaisesRegex(ValueError,'finish'):
                    export(db,root/'full.csv')
                with redirect_stdout(io.StringIO()):
                    export(db,root/'sample.csv',sample=True)
                self.assertTrue(json.loads((root/'sample.sources.json').read_text())['sample'])
                self.assertEqual(db.execute('SELECT COUNT(*) FROM state WHERE next_url IS NOT NULL').fetchone()[0],2)
            finally:
                db.close()

    def test_sample_build_and_visible_limitations(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); csv_path=root/'opinions.csv'; artifact=root/'sample.sqlite'
            pd.DataFrame(dict(citation=['']*4,case_name=['One','Two','Three','Four'],
                opinion=['marriage equality','gun control','tax policy','environment protection'],
                date_filed=['2015-06-22']*4)).to_csv(csv_path,index=False)
            with redirect_stdout(io.StringIO()):
                build_sample(csv_path,Path(__file__).resolve().parents[1]/'data',artifact)
            response=create_app(artifact).test_client().get('/?q1=marriage')
            self.assertEqual(response.status_code,200)
            self.assertIn(b'Real-data sample: 4 opinions',response.data)
            self.assertIn(b'public-opinion trends await review',response.data)
            self.assertNotIn(b'Demonstration data',response.data)
