import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scvpublic.courtlistener import download, export, initial_url, open_cache, safe_url, save_page


class CourtListenerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = open_cache(self.root/'cache.sqlite')
        self.addCleanup(self.db.close)

    def test_credentials_are_restricted_to_api_origin(self):
        for url in ['http://www.courtlistener.com/api/rest/v4/opinions/',
                    'https://other.example/api/rest/v4/opinions/',
                    'https://www.courtlistener.com/other',
                    'https://www.courtlistener.com@other.example/api/rest/v4/']:
            with self.assertRaises(ValueError):
                safe_url(url)
        self.assertEqual(safe_url(initial_url('opinions')),initial_url('opinions'))

    def test_transactional_checkpoint_and_resume(self):
        next_url=initial_url('clusters')+'&cursor=next'
        page=json.dumps(dict(results=[dict(id=1,case_name='Example')],next=next_url)).encode()
        save_page(self.db,'clusters',initial_url('clusters'),page)
        with self.assertRaises(Exception):
            save_page(self.db,'clusters',next_url,page)
        self.assertEqual(self.db.execute('SELECT pages,rows FROM state').fetchone(),(1,1))
        final=json.dumps(dict(results=[dict(id=2)],next=None)).encode()
        with patch('scvpublic.courtlistener.request_page',return_value=final) as get:
            self.assertFalse(download(self.db,'FAKE_TEST_VALUE',max_pages=1,delay=0))
            self.assertEqual(get.call_args.args[0],next_url)
        self.assertEqual(self.db.execute('SELECT pages,rows FROM state').fetchone(),(2,2))
        self.assertNotIn('FAKE_TEST_VALUE',str(self.db.execute('SELECT * FROM pages').fetchall()))

    def test_completed_crawl_exports_joined_corpus(self):
        cluster=dict(id=7,case_name='Example',date_filed='2000-01-01',citations=[dict(reporter='U.S.',volume=123,page=456)])
        opinion=dict(id=9,cluster='https://www.courtlistener.com/api/rest/v4/clusters/7/',plain_text='Realistic fixture text',type='010combined')
        for kind,row in [('clusters',cluster),('opinions',opinion)]:
            save_page(self.db,kind,initial_url(kind),json.dumps(dict(results=[row],next=None)).encode())
        export(self.db,self.root/'opinions.csv')
        text=(self.root/'opinions.csv').read_text()
        self.assertIn('123 U.S. 456',text)
        self.assertIn('Realistic fixture text',text)
        self.assertTrue((self.root/'opinions.sources.json').exists())

    def test_incomplete_crawl_cannot_publish(self):
        with self.assertRaisesRegex(ValueError,'finish'):
            export(self.db,self.root/'opinions.csv')
