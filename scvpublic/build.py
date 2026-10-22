"""Offline artifact generation. Run on a workstation, not the serving VPS."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import tempfile
from datetime import datetime
from .store import SCHEMA


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def normalize_name(value):
    return str(value).lower().strip().replace(',', '').replace("'", '').replace('versus', 'v').replace('vs.', 'v.').replace('.', '').replace(' ', '-')


def case_payload(row):
    try:
        decision_date = datetime.strptime(row['dateDecision'], '%m/%d/%Y')
        year = decision_date.year
    except (ValueError, TypeError):
        return None
    try:
        majority, minority = float(row['majVotes']), float(row['minVotes'])
        direction = {1: -1, 2: 1, 3: 0}.get(float(row['decisionDirection']))
        total = majority + minority
        value = direction * abs(majority-minority)/total if direction is not None and total > 0 else None
        if value is not None and not math.isfinite(value):
            value = None
    except (ValueError, TypeError):
        value = None
    return dict(name=row['caseName'], year=year, polarity=value, date_decision=decision_date.date().isoformat())


def case_lookup(root):
    citations, names = {}, {}
    for filename in ['scdb_legacy_case_data.csv', 'scdb_case_data.csv']:
        with open(root / 'scdb' / filename, encoding='cp1252', newline='') as stream:
            for row in csv.DictReader(stream):
                payload = case_payload(row)
                if payload:
                    if row['usCite']:
                        citations.setdefault(row['usCite'], []).append(payload)
                    names.setdefault(normalize_name(row['caseName']), []).append(payload)
    return citations, names


def court_documents(ids, root):
    citations, names = case_lookup(root)
    for key in ids:
        citation, _, name = str(key).partition('|')
        yield dict(name=name, citation=citation,
                   cases=citations.get(citation) or names.get(normalize_name(name), []))


def public_documents(codebook, responses, labels):
    import pandas as pd
    label_map = labels.dropna(subset=['vcf_code']).set_index('vcf_code')['ques_class']
    if not label_map.index.is_unique:
        raise ValueError('Duplicate question labels')
    years = pd.to_numeric(responses['VCF0004'].astype(object), errors='raise')
    for _, question in codebook.iterrows():
        code = str(question['vcf_code'])
        orientation = label_map.get(code, float('nan'))
        averages = {}
        if code in responses and orientation in (-1, 0, 1):
            answers = responses[code]
            if isinstance(answers.dtype, pd.CategoricalDtype) and len(answers.cat.categories) > 1:
                # Preserve original pandas category ordering and unweighted response scaling.
                codes = answers.cat.codes.astype(float)
                scaled = (2 * codes / (len(answers.cat.categories)-1) - 1) * orientation
                scaled[codes < 0] = float('nan')
                avg = scaled.groupby(years).mean().dropna()
                averages = {str(int(year)): float(value) for year, value in avg.items()}
        yield dict(code=code, question=str(question['question']) if pd.notna(question['question']) else '',
                   orientation=float(orientation) if pd.notna(orientation) else None, years=averages)


def write_index(db, corpus, matrix, vocabulary, documents):
    if matrix.shape != (len(documents), len(vocabulary)):
        raise ValueError(f'{corpus}: matrix/mapping dimensions do not match')
    matrix = matrix.tocsc()
    matrix.sum_duplicates()
    db.executemany('INSERT INTO documents VALUES (?,?,?)',
                   ((corpus, i, json.dumps(doc, allow_nan=False)) for i, doc in enumerate(documents)))
    for col, term in enumerate(vocabulary):
        start, end = matrix.indptr[col:col+2]
        db.executemany('INSERT INTO postings VALUES (?,?,?,?)',
                       ((corpus, str(term), int(row), float(weight))
                        for row, weight in zip(matrix.indices[start:end], matrix.data[start:end]) if weight > 0))
    db.commit()


def build(args):
    import pandas as pd
    import scipy.sparse
    from sklearn.feature_extraction.text import TfidfVectorizer
    root = args.data.resolve()
    sources = [root / 'anes/codebook/formatted_anes_codebook.csv', root / 'anes/classified_questions.csv',
               root / 'scdb/scdb_case_data.csv', root / 'scdb/scdb_legacy_case_data.csv', args.anes]
    sources += ([args.opinions] if args.opinions else [
        root / f'tf-idf/{corpus}/{name}' for corpus in ['scotus_opinion', 'public_opinion']
        for name in ['tfidf_matrix.npz', 'tfidf_rows.csv', 'tfidf_cols.csv']])
    missing = [str(p) for p in sources if not p.is_file()]
    if missing:
        raise ValueError('Missing inputs:\n' + '\n'.join(missing))
    book = pd.read_csv(sources[0])
    labels = pd.read_csv(sources[1])
    # Load only relevant columns, but keep full categorical definitions for legacy parity.
    with pd.read_stata(args.anes, iterator=True) as reader:
        available = set(reader.variable_labels())
    columns = sorted((set(book.vcf_code.dropna()) & available) | {'VCF0004'})
    responses = pd.read_stata(args.anes, columns=columns)
    if not args.allow_new_anes and pd.to_numeric(responses['VCF0004'].astype(object)).max() > 2016:
        raise ValueError('ANES extends beyond the historical 2016 dataset. Use matching historical data, or explicitly pass --allow-new-anes after reviewing the codebook.')
    public = list(public_documents(book, responses, labels))
    del responses
    if args.opinions:
        opinions = pd.read_csv(args.opinions).fillna('')
        court_ids = [f'{r.citation}|{r.case_name}' for r in opinions.itertuples()]
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), stop_words='english', min_df=.00001, max_df=.30)
        cm = vectorizer.fit_transform(opinions.opinion)
        cv = vectorizer.get_feature_names_out()
        del opinions
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=.0001, max_df=.30)
        pm = vectorizer.fit_transform(book.question.fillna(''))
        pv = vectorizer.get_feature_names_out()
    else:
        def load(corpus):
            path = root / 'tf-idf' / corpus
            return (scipy.sparse.load_npz(path/'tfidf_matrix.npz'),
                    pd.read_csv(path/'tfidf_cols.csv', keep_default_na=False)['0'].tolist(),
                    pd.read_csv(path/'tfidf_rows.csv', keep_default_na=False)['0'].tolist())
        cm, cv, court_ids = load('scotus_opinion')
        pm, pv, public_ids = load('public_opinion')
        if public_ids != book.vcf_code.fillna('nan').astype(str).tolist():
            raise ValueError('Public TF-IDF row mapping does not match codebook order')
    court = list(court_documents(court_ids, root))
    source_hashes = {str(p.resolve()): digest(p) for p in sources}
    return cm, cv, court, pm, pv, public, source_hashes


def publish(output, dataset, demo, matrices, extra=None):
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix='.build-', suffix='.sqlite', dir=output.parent)
    os.close(handle)
    try:
        with sqlite3.connect(name) as db:
            db.executescript(SCHEMA)
            cm, cv, court, pm, pv, public, hashes = matrices
            write_index(db, 'court', cm, cv, court)
            write_index(db, 'public', pm, pv, public)
            info = dict(schema_version=1, dataset=dataset, demo=demo, methodology='legacy-v1',
                        sources=hashes, court_documents=len(court), public_documents=len(public),
                        matched_court_documents=sum(bool(d['cases']) for d in court),
                        plottable_questions=sum(bool(d['years']) for d in public))
            info.update(extra or {})
            db.executemany('INSERT INTO meta VALUES (?,?)', ((k, json.dumps(v)) for k,v in info.items()))
            db.commit()
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Artifact integrity check failed')
        os.replace(name, output)
        print(json.dumps(dict(info, artifact=str(output), bytes=output.stat().st_size), indent=2))
    finally:
        Path(name).unlink(missing_ok=True)


def demo_matrices():
    import scipy.sparse
    court = [dict(name=f'Synthetic marriage case {i}', citation='', cases=[dict(name=f'Synthetic case {i}',year=year,polarity=value)]) for i,(year,value) in enumerate([(1980,-.6),(2000,0),(2016,.6)])]
    public = [dict(code='DEMO',question='Synthetic question: support marriage equality?',orientation=1,
                   years={'1980':-.5,'2000':.1,'2016':.7})]
    return scipy.sparse.csr_matrix([[.5],[.7],[.8]]), ['marriage'], court, scipy.sparse.csr_matrix([[.8]]), ['marriage'], public, {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('data'))
    parser.add_argument('--anes', type=Path, default=Path('data/anes/anes_timeseries_cdf.dta'))
    parser.add_argument('--opinions', type=Path, help='Normalized opinion CSV; omit to import existing NPZ matrices')
    parser.add_argument('--output', type=Path, default=Path('artifacts/search.sqlite'))
    parser.add_argument('--dataset', default='Historical reconstruction')
    parser.add_argument('--demo', action='store_true', help='Build explicitly labeled synthetic fixture')
    parser.add_argument('--allow-new-anes', action='store_true')
    args = parser.parse_args()
    try:
        matrices = demo_matrices() if args.demo else build(args)
        import importlib.metadata
        versions = {p: importlib.metadata.version(p) for p in ['numpy','scipy','pandas','scikit-learn']}
        publish(args.output, args.dataset if not args.demo else 'Synthetic demonstration', args.demo, matrices,
                {'build_versions': versions, 'allow_new_anes': args.allow_new_anes})
    except (ValueError, FileNotFoundError) as error:
        parser.exit(2, f'{error}\n')


if __name__ == '__main__':
    main()
