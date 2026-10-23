import os
from contextlib import closing
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request
from .chart import chart
from .store import connect, metadata, search, survey_search, series, court_counts


def create_app(artifact=None, hybrid_dir=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 4096
    path = Path(artifact or os.environ.get('SCVPO_ARTIFACT', 'artifacts/search.sqlite'))
    # Fail fast for missing/incompatible artifacts rather than serving a broken app.
    with closing(connect(path)) as db:
        info = metadata(db)
        if info.get('schema_version') != 1:
            raise RuntimeError('Unsupported artifact schema; rebuild with python -m scvpublic.build')
    app.config['ARTIFACT'] = path
    hybrid_dir = hybrid_dir or os.environ.get('SCVPO_HYBRID')
    hybrid = None
    if hybrid_dir:
        from .hybrid import HybridSearch, CHART_CUTOFF
        hybrid = HybridSearch(hybrid_dir, path)
        info['hybrid_search'] = True
        info['court_chart_cutoff'] = CHART_CUTOFF
    app.config['SEARCH_MODE'] = 'hybrid' if hybrid else 'tfidf'
    @app.after_request
    def headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        return response

    @app.get('/healthz')
    def health():
        try:
            with closing(connect(path)) as db:
                db.execute('SELECT 1 FROM meta LIMIT 1').fetchone()
            return {'status': 'ok', 'dataset': info.get('dataset'), 'search_mode': app.config['SEARCH_MODE']}
        except sqlite3.Error:
            return {'status': 'unavailable'}, 503

    @app.get('/')
    def index():
        terms = [request.args.get(f'q{i}', '').strip().lower() for i in range(1, 4)]
        counts = {}
        error = None
        court, public, gss, svg = [], [], [], ''
        if any(len(t) > 100 for t in terms):
            error = 'Each keyword or phrase must be at most 100 characters.'
        elif any(terms):
            with closing(connect(path)) as db:
                public = survey_search(db, 'public', terms)
                if hybrid:
                    from .hybrid import chart_matches
                    candidates = hybrid.search(terms)
                    court = candidates[:10]
                    trend_court = chart_matches(candidates)
                else:
                    court = search(db, 'court', terms)
                    trend_court = search(db, 'court', terms, limit=None, relative_cutoff=0.20)
                if info.get('gss_documents'):
                    gss = survey_search(db, 'gss', terms)
            counts = court_counts(trend_court)
            svg = chart(*series(trend_court, public), counts=counts,
                        gss=series([], gss)[1] if info.get('gss_documents') else None)
        return render_template('index.html', terms=terms, court=court, public=public,
                               svg=svg, info=info, error=error, searched=any(terms),
                               counts=counts, gss=gss), (400 if error else 200)
    return app
