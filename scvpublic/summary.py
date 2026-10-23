"""Offline summary TF-IDF candidate; preserves survey indexes and case payloads."""
import argparse
from collections import defaultdict, Counter
from contextlib import closing
import csv
import json
from pathlib import Path
import sqlite3
import pyarrow as pa
from .build import digest, write_index
from .casesumm import FILES, citation_key, resolve, court_vectorizer
from .store import connect, SCHEMA


def source_texts(artifact):
    with closing(connect(artifact)) as db:
        docs = [dict(json.loads(p), doc_id=i) for i,p in db.execute("SELECT id,payload FROM documents WHERE corpus='court' ORDER BY id")]
        source_hashes = json.loads(db.execute("SELECT value FROM meta WHERE key='sources'").fetchone()[0])
    wanted = {d['case_id'] for d in docs}
    citations, dockets = defaultdict(list), defaultdict(list)
    scdb = Path('data/raw/scdb-2026/SCDB_2026_01_caseCentered_Citation.csv')
    if digest(scdb) != source_hashes[str(scdb.resolve())]: raise ValueError('SCDB checksum mismatch')
    with scdb.open(encoding='utf-8-sig') as stream:
        for row in csv.DictReader(stream):
            citations[citation_key(row['usCite'])].append(row)
            dockets[(row['term'], row['docket'])].append(row)
    texts = {}
    origins = {}
    for name, checksum in FILES.items():
        path = Path('data/raw/casesumm')/name
        if digest(path) != checksum: raise ValueError('CaseSumm checksum mismatch')
        with pa.memory_map(str(path), 'r') as stream:
            for batch in pa.ipc.open_stream(stream):
                for record in batch.to_pylist():
                    doc, _ = resolve(record['citation'], citations, dockets)
                    if doc and doc['case_id'] in wanted:
                        texts[doc['case_id']] = record['syllabus'] or record['opinion']
                        origins[doc['case_id']] = 'syllabus' if record['syllabus'] else 'opinion_fallback'
    official = Path('data/processed/modern/official.json')
    if digest(official) != source_hashes[str(official.resolve())]: raise ValueError('Supplement checksum mismatch')
    for record in json.loads(official.read_text())['records']:
        if record.get('unscored'): key = record['case_id']
        else:
            doc, _ = resolve(record['citation'], citations, dockets)
            key = doc['case_id'] if doc else None
        if key in wanted and key not in texts:
            texts[key] = record['opinion']
            origins[key] = 'official_opinion_fallback'
    if set(texts) != wanted: raise ValueError('Incomplete summary coverage')
    return docs, texts, origins


def build(artifact, output):
    if output.exists():
        raise FileExistsError(output)
    docs, texts, origins = source_texts(artifact)
    vectorizer = court_vectorizer()
    matrix = vectorizer.fit_transform(texts[d['case_id']] for d in docs)
    output.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(output)) as db:
        db.executescript(SCHEMA)
        db.execute('ATTACH DATABASE ? AS base', (str(artifact.resolve()),))
        db.execute('INSERT INTO meta SELECT * FROM base.meta')
        db.execute("INSERT INTO documents SELECT * FROM base.documents WHERE corpus != 'court'")
        db.execute("INSERT INTO postings SELECT * FROM base.postings WHERE corpus != 'court'")
        for d in docs:
            d.pop('doc_id')
        write_index(db, 'court', matrix, vectorizer.get_feature_names_out(), docs)
        info = dict(base_sha256=digest(artifact), text_sources=dict(Counter(origins.values())),
                    ngram_range=[1,2], documents=len(docs), postings=matrix.nnz,
                    description='Full CaseSumm syllabuses; full opinion fallback where no syllabus exists')
        db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ('court_summary_index', json.dumps(info)))
        db.commit()
    print(json.dumps(info, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, default=Path('artifacts/gss-bigram.sqlite'))
    parser.add_argument('--output', type=Path, default=Path('artifacts/gss-summary.sqlite'))
    args = parser.parse_args()
    build(args.artifact, args.output)


if __name__ == '__main__': main()
