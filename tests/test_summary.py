import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from scvpublic.store import SCHEMA, connect, search
from scvpublic.summary import build


class SummaryTests(unittest.TestCase):
    def test_replaces_only_court_index_and_preserves_payloads(self):
        with tempfile.TemporaryDirectory() as directory:
            base, output = [Path(directory)/name for name in ('base.sqlite','summary.sqlite')]
            payload = dict(case_id='one', name='Example', cases=[])
            with sqlite3.connect(base) as db:
                db.executescript(SCHEMA)
                db.execute('INSERT INTO meta VALUES (?,?)', ('schema_version','1'))
                for corpus in ('court','public','gss'):
                    db.execute('INSERT INTO documents VALUES (?,?,?)', (corpus,0,json.dumps(payload)))
                    db.execute('INSERT INTO postings VALUES (?,?,?,?)', (corpus,'old',0,0.5))
            with patch('scvpublic.summary.source_texts', return_value=([dict(payload,doc_id=0)], {'one':'birth control contraception'}, {'one':'syllabus'})):
                build(base, output)
            with connect(output) as db:
                self.assertEqual(search(db,'court',['old']), [])
                self.assertEqual(search(db,'court',['birth control'])[0]['case_id'], 'one')
                for corpus in ('public','gss'):
                    self.assertEqual(search(db,corpus,['old'])[0]['score'], .5)
                self.assertEqual(json.loads(db.execute("SELECT payload FROM documents WHERE corpus='court'").fetchone()[0]), payload)
            with self.assertRaises(FileExistsError): build(base, output)
