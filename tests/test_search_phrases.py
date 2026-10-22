import sqlite3
import unittest
from scipy.sparse import csr_matrix
from scvpublic.build import write_index
from scvpublic.store import SCHEMA,search


class PhraseTests(unittest.TestCase):
    def test_multiword_queries_find_unigrams_and_boost_public_bigrams(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript(SCHEMA)
            for corpus in ['court','public']:
                write_index(db,corpus,csr_matrix([[.4,.4,.8],[.7,0,0]]),
                            ['gun','control','gun control'],[{'id':0},{'id':1}])
            self.assertEqual([d['id'] for d in search(db,'court',['Gun control!'])],[0,1])
            self.assertAlmostEqual(search(db,'court',['gun control'])[0]['score'],.8)
            self.assertAlmostEqual(search(db,'public',['gun control'])[0]['score'],1.6)
            self.assertEqual(search(db,'court',['!!!']),[])
