from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import Mock
import numpy as np
from scvpublic.expansion import ExpandedSearch,phrase_matches
from scvpublic.store import SCHEMA,connect


class ExpansionTests(unittest.TestCase):
    def test_complete_phrase_gate_expansion_weight_and_deduplication(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'search.sqlite'
            with sqlite3.connect(path) as db:
                db.executescript(SCHEMA)
                db.execute("CREATE VIRTUAL TABLE court_phrases USING fts5(text, tokenize='unicode61')")
                for i,text in enumerate(['birth control contraceptive','contraceptives','corporate control','birth followed by control']):
                    db.execute('INSERT INTO documents VALUES (?,?,?)',('court',i,json.dumps(dict(case_id=str(i),name=str(i),cases=[]))))
                    db.execute('INSERT INTO court_phrases(rowid,text) VALUES (?,?)',(i,text))
                db.executemany('INSERT INTO postings VALUES (?,?,?,?)',[
                    ('court','birth control',0,1.),('court','contraceptive',0,1.),
                    ('court','contraceptives',1,1.),('court','control',2,5.),('court','birth',3,5.)])
            engine=object.__new__(ExpandedSearch)
            engine.artifact=path;engine.lock=threading.Lock()
            engine.terms=['contraceptive'];engine.vectors=np.array([[1.,0.]])
            engine.encoder=Mock();engine.encoder.encode.return_value=np.array([[.9,0.]])
            hits,expanded=engine.search(['birth control'])
            self.assertEqual([h['case_id'] for h in hits],['0','1'])
            self.assertEqual(hits[1]['score'],.5)
            self.assertEqual(expanded[0]['alternatives'],['contraceptive'])
            self.assertEqual(engine.search(['!!!']),([],[]))
            with closing(connect(path)) as db:
                self.assertEqual(phrase_matches(db,'birth control'),{0})
                self.assertEqual(phrase_matches(db,'" OR *'),set())
            engine.encoder.encode.return_value=np.array([[.1,0.]])
            hits,expanded=engine.search(['unseen'])
            self.assertEqual(hits,[])
            self.assertEqual(expanded[0]['alternatives'],[])
