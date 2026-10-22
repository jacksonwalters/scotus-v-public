"""Report artifact size, provenance, integrity and a representative query time."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import time
from .store import connect, metadata, search


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact', type=Path)
    parser.add_argument('--term', default='marriage')
    args = parser.parse_args()
    with closing(connect(args.artifact)) as db:
        start = time.perf_counter()
        counts = {corpus: len(search(db, corpus, [args.term])) for corpus in ['court','public']}
        result = dict(metadata(db), bytes=args.artifact.stat().st_size, query_seconds=time.perf_counter()-start,
                      hits=counts, integrity=db.execute('PRAGMA integrity_check').fetchone()[0])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
