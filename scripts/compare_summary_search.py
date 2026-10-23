"""Compare fixed Court retrieval rules on full opinions and summaries."""
import json
from contextlib import closing
from pathlib import Path
from scvpublic.store import connect, search

QUERIES = ['birth control', 'civil rights', 'gun control', 'gay marriage', 'abortion', 'health care', 'zzzznomatchzzzz']

def main():
    result = {}
    for label, artifact in [('opinions','artifacts/gss-bigram.sqlite'), ('summaries','artifacts/gss-summary.sqlite')]:
        with closing(connect(artifact)) as db:
            result[label] = {}
            for query in QUERIES:
                hits = search(db, 'court', [query], limit=None, relative_cutoff=.20)
                result[label][query] = dict(count=len(hits), hits=[dict(case_id=h['case_id'], name=h['name'], score=h['score']) for h in hits])
    Path('artifacts/summary-comparison.json').write_text(json.dumps(result, indent=2)+'\n')
    for query in QUERIES:
        print('\n'+query)
        for label in result:
            r=result[label][query]
            print(label, r['count'])
            for h in r['hits'][:10]: print(' ', h['case_id'], h['name'], round(h['score'],4))

if __name__ == '__main__': main()
