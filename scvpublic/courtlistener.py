"""Resumable SCOTUS-only acquisition through the official CourtListener v4 API.

Raw responses, page cursors and checksums are stored in a local SQLite cache.
Credentials are read locally and sent only to the fixed CourtListener API origin.
"""
import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://www.courtlistener.com/api/rest/v4/'
FIELDS = {
    'clusters': 'id,case_name,case_name_full,date_filed,citations,docket,sub_opinions',
    'opinions': 'id,cluster,type,html_with_citations,html,html_lawbox,html_columbia,html_anon_2020,plain_text,absolute_url',
}


def initial_url(kind, date_from=None, date_to=None):
    court_field = 'docket__court' if kind == 'clusters' else 'cluster__docket__court'
    params = {court_field: 'scotus', 'order_by': 'id', 'fields': FIELDS[kind]}
    if date_from:
        field = 'date_filed' if kind == 'clusters' else 'cluster__date_filed'
        params.update({field+'__gte': date_from, field+'__lte': date_to})
    return BASE + kind + '/?' + urllib.parse.urlencode(params)


def safe_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.netloc != 'www.courtlistener.com' or not parsed.path.startswith('/api/rest/v4/'):
        raise ValueError('Refusing to send credentials outside the CourtListener API')
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected API redirect; refusing to forward credentials')


def request_page(url, token):
    opener = urllib.request.build_opener(NoRedirect)
    for attempt in range(6):
        request = urllib.request.Request(safe_url(url), headers={
            'Authorization': 'Token ' + token, 'Accept': 'application/json',
            'User-Agent': 'scotus-v-public research rebuild',
        })
        try:
            with opener.open(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code in (401, 403):
                raise RuntimeError(f'CourtListener HTTP {error.code}: check token and API access') from None
            if error.code not in (429, 500, 502, 503, 504):
                raise RuntimeError(f'CourtListener HTTP {error.code}') from None
            retry = error.headers.get('Retry-After', '')
            delay = max(2**attempt, float(retry) if retry.isdigit() else 0)
            if delay > 60:
                raise RuntimeError(f'CourtListener asks us to wait {delay:.0f}s; checkpoint saved. Resume later or arrange higher API limits.') from None
            print(f'HTTP {error.code}; retry in {delay:.0f}s (checkpoint retained)', flush=True)
        except (urllib.error.URLError, TimeoutError):
            delay = 2**attempt
            print(f'Connection interrupted; retry in {delay}s (checkpoint retained)', flush=True)
        if attempt == 5:
            raise RuntimeError('Download stopped after repeated request failures; rerun to resume')
        time.sleep(delay)


def open_cache(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.executescript('''
        CREATE TABLE IF NOT EXISTS state(kind TEXT PRIMARY KEY, next_url TEXT, pages INTEGER, rows INTEGER);
        CREATE TABLE IF NOT EXISTS records(kind TEXT,id INTEGER,payload BLOB,PRIMARY KEY(kind,id)) WITHOUT ROWID;
        CREATE TABLE IF NOT EXISTS pages(kind TEXT,number INTEGER,url TEXT,sha256 TEXT,retrieved TEXT,PRIMARY KEY(kind,number));
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    ''')
    return db


def save_page(db, kind, url, raw):
    data = json.loads(raw)
    if not isinstance(data.get('results'), list) or 'next' not in data:
        raise ValueError('Unexpected API page format')
    next_url = data['next']
    if next_url:
        safe_url(next_url)
        if next_url == url:
            raise ValueError('API returned a repeated cursor')
    state = db.execute('SELECT pages,rows FROM state WHERE kind=?', (kind,)).fetchone()
    page, total = state or (0, 0)
    with db:
        for row in data['results']:
            db.execute('INSERT INTO records VALUES (?,?,?)',
                       (kind, row['id'], gzip.compress(json.dumps(row).encode(), mtime=0)))
        db.execute('INSERT INTO pages VALUES (?,?,?,?,?)',
                   (kind, page+1, url, hashlib.sha256(raw).hexdigest(), datetime.now(timezone.utc).isoformat()))
        db.execute('INSERT OR REPLACE INTO state VALUES (?,?,?,?)',
                   (kind, next_url, page+1, total+len(data['results'])))
    return len(data['results'])


def set_scope(db, date_from, date_to):
    bounds = json.dumps([date_from, date_to])
    prior = db.execute("SELECT value FROM settings WHERE key='dates'").fetchone()
    if (prior and prior[0] != bounds) or (not prior and date_from and db.execute('SELECT 1 FROM state').fetchone()):
        raise ValueError('Date range differs from cached crawl; use a separate --cache')
    with db:
        db.execute("INSERT OR IGNORE INTO settings VALUES ('dates',?)", (bounds,))


def download(db, token, max_pages=0, delay=1, date_from=None, date_to=None):
    set_scope(db, date_from, date_to)
    completed_pages = 0
    for kind in FIELDS:
        state = db.execute('SELECT next_url,pages,rows FROM state WHERE kind=?', (kind,)).fetchone()
        url = state[0] if state else initial_url(kind, date_from, date_to)
        while url:
            if max_pages and completed_pages >= max_pages:
                return False
            raw = request_page(url, token)
            save_page(db, kind, url, raw)
            completed_pages += 1
            url, pages, rows = db.execute('SELECT next_url,pages,rows FROM state WHERE kind=?', (kind,)).fetchone()
            if pages == 1 or pages % 10 == 0 or not url:
                print(f'{kind}: {rows:,} records, {pages:,} pages; ' + ('complete' if not url else 'downloading'), flush=True)
            time.sleep(delay)
    return True


def resource_id(value):
    return int(str(value).rstrip('/').rsplit('/', 1)[-1])


def export(db, output, sample=False):
    from .ingest import opinion_text
    from .build import digest
    states = db.execute('SELECT kind,next_url,pages,rows FROM state').fetchall()
    if not sample and {s[0] for s in states if s[1] is None} != set(FIELDS):
        raise ValueError('Both API streams must finish before publishing a corpus')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.with_suffix('.csv.partial')
    missing = empty = count = 0
    try:
        with staging.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['citation', 'case_name', 'opinion', 'opinion_id', 'cluster_id', 'date_filed', 'opinion_type'])
            writer.writeheader()
            for opinion_id, payload in db.execute("SELECT id,payload FROM records WHERE kind='opinions' ORDER BY id"):
                row = json.loads(gzip.decompress(payload))
                cluster_id = resource_id(row['cluster'])
                match = db.execute("SELECT payload FROM records WHERE kind='clusters' AND id=?", (cluster_id,)).fetchone()
                if not match:
                    missing += 1
                    continue
                cluster = json.loads(gzip.decompress(match[0]))
                citation = next((f"{c['volume']} U.S. {c['page']}" for c in cluster.get('citations', []) if c.get('reporter') == 'U.S.'), '')
                text = opinion_text(row)
                empty += not bool(text.strip())
                writer.writerow(dict(citation=citation, case_name=cluster.get('case_name') or cluster.get('case_name_full') or '',
                                     opinion=text, opinion_id=opinion_id, cluster_id=cluster_id,
                                     date_filed=cluster.get('date_filed'), opinion_type=row.get('type')))
                count += 1
        if (missing and not sample) or not count:
            raise ValueError(f'Corpus not published: {missing} opinions lack clusters; {count} matched')
        staging.replace(output)
    finally:
        staging.unlink(missing_ok=True)
    report = dict(source='CourtListener API v4', court='scotus', acquisition='Live API crawl; not a transactional snapshot',
                  rows=count, empty_text_rows=empty, sha256=digest(output),
                  sample=sample, unmatched_opinions_excluded=missing,
                  streams={s[0]:dict(pages=s[2],records=s[3],initial_url=db.execute('SELECT url FROM pages WHERE kind=? ORDER BY number LIMIT 1',(s[0],)).fetchone()[0]) for s in states},
                  started=db.execute('SELECT MIN(retrieved) FROM pages').fetchone()[0],
                  finished=db.execute('SELECT MAX(retrieved) FROM pages').fetchone()[0])
    output.with_suffix('.sources.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token-file', type=Path, default=Path('.courtlistener-token'))
    parser.add_argument('--cache', type=Path, default=Path('data/raw/rebuild/courtlistener.sqlite'))
    parser.add_argument('--output', type=Path, default=Path('data/raw/rebuild/scotus_opinions.csv'))
    parser.add_argument('--max-pages', type=int, default=0, help='Stop after N new pages; zero downloads all')
    parser.add_argument('--delay', type=float, default=13, help='Seconds between requests; honors server throttling')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--usage', action='store_true', help='Read account rate limits without downloading pages')
    parser.add_argument('--date-from', help='Inclusive decision date YYYY-MM-DD')
    parser.add_argument('--date-to', help='Inclusive decision date YYYY-MM-DD')
    parser.add_argument('--sample', action='store_true', help='Fetch at most one page per stream, then export available matched opinions as an explicitly partial sample')
    args = parser.parse_args()
    if bool(args.date_from) != bool(args.date_to):
        parser.error('Supply both --date-from and --date-to')
    if args.date_from:
        try:
            start = datetime.strptime(args.date_from, '%Y-%m-%d')
            end = datetime.strptime(args.date_to, '%Y-%m-%d')
            if start > end:
                raise ValueError()
        except ValueError:
            parser.error('Invalid or reversed date range; use YYYY-MM-DD')
    db = open_cache(args.cache)
    try:
        if args.status:
            print(json.dumps([dict(kind=s[0],complete=s[1] is None,pages=s[2],records=s[3])
                              for s in db.execute('SELECT * FROM state')], indent=2))
            return
        token = os.environ.get('COURTLISTENER_TOKEN') or args.token_file.read_text().strip()
        if not token or any(c.isspace() for c in token):
            raise ValueError('Token must be a nonempty single value')
        if args.usage:
            data = json.loads(request_page(BASE + 'api-usage/', token))
            print(json.dumps({'limits': [r for r in data.get('current_usage', []) if r['scope'] == 'user']}, indent=2))
            return
        if args.sample:
            if not args.date_from:
                raise ValueError('Sample mode requires explicit date bounds and a separate cache/output')
            if args.output == Path('data/raw/rebuild/scotus_opinions.csv') or args.cache == Path('data/raw/rebuild/courtlistener.sqlite'):
                raise ValueError('Sample mode requires separate --cache and --output paths')
            set_scope(db, args.date_from, args.date_to)
            for kind in FIELDS:
                if not db.execute('SELECT 1 FROM state WHERE kind=?', (kind,)).fetchone():
                    url = initial_url(kind, args.date_from, args.date_to)
                    save_page(db, kind, url, request_page(url, token))
                    time.sleep(args.delay)
            export(db, args.output, sample=True)
            return
        if download(db, token, args.max_pages, args.delay, args.date_from, args.date_to):
            export(db, args.output)
        else:
            print('Page limit reached; rerun the same command without --max-pages to continue', flush=True)
    except (ValueError, RuntimeError, OSError) as error:
        parser.exit(2, str(error)+'\n')
    finally:
        db.close()


if __name__ == '__main__':
    main()
