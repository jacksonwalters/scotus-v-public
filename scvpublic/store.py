"""Disk-backed inverted TF-IDF index. No corpus or matrix in web RAM."""
import json
import re
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE documents (
 corpus TEXT NOT NULL, id INTEGER NOT NULL, payload TEXT NOT NULL,
 PRIMARY KEY (corpus,id)
) WITHOUT ROWID;
CREATE TABLE postings (
 corpus TEXT NOT NULL, term TEXT NOT NULL, doc INTEGER NOT NULL, weight REAL NOT NULL,
 PRIMARY KEY (corpus,term,doc)
) WITHOUT ROWID;
"""


def connect(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    db.execute('PRAGMA query_only=ON')
    db.execute('PRAGMA cache_size=-8192')
    db.execute('PRAGMA temp_store=FILE')
    return db


def metadata(db):
    return {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM meta')}


def search(db, corpus, terms):
    # UNION ALL preserves repeated-keyword weighting in the original application.
    expanded = []
    for phrase in terms:
        words = re.findall(r'(?u)\b\w+\b', phrase.lower())
        expanded.extend(words)
        if corpus == 'public':
            expanded.extend(' '.join(pair) for pair in zip(words, words[1:]))
    terms = expanded
    if not terms:
        return []
    clauses = ['SELECT doc,weight FROM postings WHERE corpus=? AND term=?'] * len(terms)
    args = [x for term in terms for x in (corpus, term)]
    hits = db.execute('SELECT doc,SUM(weight) AS score FROM (' +
                      ' UNION ALL '.join(clauses) +
                      ') GROUP BY doc ORDER BY score DESC,doc ASC LIMIT 10', args)
    return [dict(json.loads(db.execute(
        'SELECT payload FROM documents WHERE corpus=? AND id=?', (corpus, doc)
    ).fetchone()[0]), score=score) for doc, score in hits.fetchall()]


def series(court, public):
    # Intentional legacy behavior: later ranked cases overwrite earlier same-year cases.
    sc = {}
    for opinion in court:
        for case in opinion['cases']:
            if case['polarity'] is not None:
                sc[case['year']] = case['polarity']
    values = {}
    families = {}
    superseded = {(int(year), code) for q in public for year in q['years']
                  for code in q.get('supersedes', [])}
    for question in public:
        if 'family' in question:
            for year, value in question['years'].items():
                if (int(year), question['code']) in superseded:
                    continue
                key = (int(year), question['family'])
                rank = (question.get('priority', 0), question['code'])
                if key not in families or rank > families[key][0]:
                    families[key] = (rank, value)
            continue
        for year, value in question['years'].items():
            values.setdefault(int(year), []).append(value)
    for (year, _), (_, value) in families.items():
        values.setdefault(year, []).append(value)
    po = {year: sum(v) / len(v) for year, v in values.items()}
    return dict(sorted(sc.items())), dict(sorted(po.items()))
