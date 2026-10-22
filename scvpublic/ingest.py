"""Normalize original CourtListener JSON or current bulk CSV tables offline."""
import argparse
import bz2
import csv
import gzip
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile

csv.field_size_limit(sys.maxsize)


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def opinion_text(row):
    for key in ['html_with_citations', 'html', 'html_lawbox', 'html_columbia', 'html_anon_2020']:
        if row.get(key):
            parser = Text()
            parser.feed(row[key])
            return ''.join(parser.parts).rstrip()
    return row.get('plain_text') or ''


def rows(path):
    opener = bz2.open if str(path).endswith('.bz2') else gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8', newline='') as stream:
        # CourtListener COPY export uses backslash escaping, not doubled quotes.
        yield from csv.DictReader(stream, escapechar='\\', doublequote=False, strict=True)


def legacy(directory):
    for path in sorted(directory.glob('*.json')):
        row = json.loads(path.read_text())
        text = opinion_text(row)
        citation = re.search(r'\d{1,3} U\.S\. \d{1,4}', '\n'.join(text.splitlines()[:2]))
        name = row.get('absolute_url', '').rstrip('/').rsplit('/', 1)[-1]
        yield dict(citation=citation.group() if citation else '', case_name=name, opinion=text)


def bulk(dockets, clusters, citations, opinions):
    # Bulk snapshots contain all courts; filter joins on disk before reading opinion text.
    with tempfile.TemporaryDirectory(prefix='scvpo-import-') as temp:
        with sqlite3.connect(str(Path(temp)/'join.sqlite')) as db:
            db.executescript('CREATE TABLE docket(id TEXT PRIMARY KEY); CREATE TABLE cluster(id TEXT PRIMARY KEY,name TEXT,citation TEXT);')
            db.executemany('INSERT INTO docket VALUES (?)', ((r['id'],) for r in rows(dockets) if r['court_id']=='scotus'))
            for row in rows(clusters):
                if db.execute('SELECT 1 FROM docket WHERE id=?', (row['docket_id'],)).fetchone():
                    db.execute('INSERT INTO cluster VALUES (?,?,?)', (row['id'], row.get('case_name') or row.get('case_name_full') or '', ''))
            for row in rows(citations):
                if row['reporter'] == 'U.S.':
                    db.execute('UPDATE cluster SET citation=? WHERE id=?',
                               (f"{row['volume']} U.S. {row['page']}", row['cluster_id']))
            db.commit()
            for row in rows(opinions):
                match = db.execute('SELECT name,citation FROM cluster WHERE id=?', (row['cluster_id'],)).fetchone()
                if match:
                    yield dict(citation=match[1], case_name=match[0], opinion=opinion_text(row))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json-dir', type=Path)
    for name in ['dockets', 'clusters', 'citations', 'opinions']:
        parser.add_argument('--'+name, type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    tables = [args.dockets, args.clusters, args.citations, args.opinions]
    if bool(args.json_dir) == all(tables) or (not args.json_dir and not all(tables)):
        parser.error('Choose --json-dir OR all four bulk tables')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    # Staging file avoids leaving a plausible-looking partial corpus on failure.
    with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8', dir=args.output.parent, delete=False) as stream:
        staging = Path(stream.name)
        try:
            writer = csv.DictWriter(stream, fieldnames=['citation', 'case_name', 'opinion'])
            writer.writeheader()
            for row in legacy(args.json_dir) if args.json_dir else bulk(*tables):
                writer.writerow(row)
                count += 1
            if not count:
                raise ValueError('No opinions imported')
        except BaseException:
            staging.unlink(missing_ok=True)
            raise
    staging.replace(args.output)
    from .build import digest
    inputs = sorted(args.json_dir.glob('*.json')) if args.json_dir else tables
    args.output.with_suffix('.sources.json').write_text(json.dumps({
        'inputs': {str(p): digest(p) for p in inputs}, 'output_sha256': digest(args.output),
        'rows': count, 'format': 'courtlistener-json' if args.json_dir else 'courtlistener-bulk-csv',
    }, indent=2)+'\n')
    print(f'Wrote {count} opinions to {args.output}')


if __name__ == '__main__':
    main()
