"""Build a real-opinion smoke test without using unreviewed ANES response mappings."""
import argparse
from pathlib import Path
import json
import pandas as pd
from scipy.sparse import load_npz
from sklearn.feature_extraction.text import TfidfVectorizer
from .build import court_documents, digest, publish


def build_sample(opinions_path, data, output, public_artifact=None):
    opinions = pd.read_csv(opinions_path, keep_default_na=False)
    if len(opinions) < 4:
        raise ValueError('At least four opinions are needed for the unchanged max_df=.30 setting')
    ids = [f'{r.citation}|{r.case_name}' for r in opinions.itertuples()]
    court = list(court_documents(ids, data))
    # A repeated caption (e.g. Johnson v. United States) is not a unique case.
    # Require the known decision date for this fresh sample's historical matches.
    for doc, date in zip(court, opinions.date_filed):
        doc['cases'] = [case for case in doc['cases'] if case['date_decision'] == date]
    tf = TfidfVectorizer(ngram_range=(1, 1), stop_words='english', min_df=.00001, max_df=.30)
    matrix = tf.fit_transform(opinions['opinion'])
    public_path = data/'tf-idf/public_opinion'
    book_path = data/'anes/codebook/formatted_anes_codebook.csv'
    book = pd.read_csv(book_path)
    rows = pd.read_csv(public_path/'tfidf_rows.csv',keep_default_na=False)['0'].tolist()
    if rows != book.vcf_code.fillna('nan').astype(str).tolist():
        raise ValueError('Public index row mapping differs from codebook')
    public = [dict(code=str(r.vcf_code), question='' if pd.isna(r.question) else str(r.question),
                   orientation=None, years={}) for r in book.itertuples()]
    public_matrix = load_npz(public_path/'tfidf_matrix.npz')
    vocab = pd.read_csv(public_path/'tfidf_cols.csv',keep_default_na=False)['0'].tolist()
    inputs = [opinions_path, book_path, public_path/'tfidf_matrix.npz', public_path/'tfidf_rows.csv',
              public_path/'tfidf_cols.csv', data/'scdb/scdb_case_data.csv', data/'scdb/scdb_legacy_case_data.csv']
    if public_artifact:
        payload = json.loads(public_artifact.read_text())
        if payload['methodology'] != 'explicit-anes-v1':
            raise ValueError('Unsupported public methodology')
        public = payload['documents']
        vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words='english', min_df=.0001, max_df=.30)
        public_matrix = vectorizer.fit_transform([d['title']+' '+d['question'] for d in public])
        vocab = vectorizer.get_feature_names_out()
        inputs.append(public_artifact)
    provenance = opinions_path.with_suffix('.sources.json')
    if provenance.exists():
        if json.loads(provenance.read_text())['sha256'] != digest(opinions_path):
            raise ValueError('Opinion CSV no longer matches acquisition manifest')
        inputs.append(provenance)
    hashes = {str(p.resolve()):digest(p) for p in inputs}
    if public_artifact:
        hashes.update(payload['sources'])
    publish(output, f'Real SCOTUS sample · {opinions.date_filed.min()} to {opinions.date_filed.max()}', False,
            (matrix, tf.get_feature_names_out(), court, public_matrix, vocab, public, hashes),
            {'methodology':'court-legacy-public-explicit-v1' if public_artifact else 'legacy-v1',
             'sample':True, 'public_trends_enabled':bool(public_artifact),
             'public_methodology':'explicit-anes-v1' if public_artifact else None,
             'sample_date_from':str(opinions.date_filed.min()), 'sample_date_to':str(opinions.date_filed.max()),
             'case_matching':'Legacy citation/name lookup, restricted to exact decision date',
             'sample_note':(f'A small Court sample, not a representative corpus. Public trends use {len(public)} explicitly mapped ANES variables, survey weights, and liberal-positive numeric scales.' if public_artifact else 'A small real-data test, not a representative corpus. Court scores use the historical SCDB snapshot. Survey questions are searchable; public-opinion trends await review of the new ANES response mappings.')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--opinions',type=Path,default=Path('data/raw/sample/scotus_opinions.csv'))
    parser.add_argument('--data',type=Path,default=Path('data'))
    parser.add_argument('--output',type=Path,default=Path('artifacts/sample.sqlite'))
    parser.add_argument('--public-artifact',type=Path)
    args = parser.parse_args()
    build_sample(args.opinions,args.data,args.output,args.public_artifact)


if __name__ == '__main__':
    main()
