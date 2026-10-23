# Local hybrid Court search

Active locally on port 8004 when started with `make serve-hybrid`. The public
VPS remains on its existing TF-IDF release. Default `make serve` also remains
TF-IDF; the `/healthz` response explicitly reports `search_mode`.

## Run

```sh
.venv/bin/pip install -r requirements-expansion.txt
make serve-hybrid
.venv/bin/python scripts/check_hybrid_http.py
```

The optional dependency file is shared with the query-expansion experiment;
query expansion, NMF and a cross-encoder are not used by this search path.
`HYBRID_ARTIFACT`, `HYBRID_BUNDLE` and `HYBRID_PORT` can override the Make defaults.
The current artifact is `artifacts/gss-pilot.sqlite` and the embedding bundle is
`artifacts/semantic-full`. Startup validates their exact hash match and the model,
vector and ID files. A mismatched artifact fails startup rather than silently
searching the wrong case mappings. To rebuild the bundle from the verified raw
sources, use `PYTHONPATH=. .venv/bin/python scripts/build_full_embeddings.py`;
the builder refuses an existing output directory.

## One retrieval pipeline

- TF-IDF on full opinions independently nominates its top 100 matches.
- Complete-summary passage embeddings independently nominate their top 100 cases,
  using maximum passage cosine per case. The 391 cases without syllabuses use
  full official-opinion text. No relative semantic cutoff discards lexical hits.
- Deduplicate the union and rank by `0.9 * max(cosine,0) + 0.1 * normalized TF-IDF`.
  TF-IDF is normalized by its best query score. Missing lexical evidence scores
  zero. No query-specific aliases or case blacklists are used.
- If there are no lexical matches anywhere, require best semantic similarity of
  at least .50. If the best combined score is below .30, abstain entirely.
- Display at most ten candidates. Independently include all candidate cases with
  combined score >= .30 in the chart, using that score as the annual case weight.
  A displayed case below this cutoff is labeled as excluded from the trend.

The weights and cutoff are provisional development choices, not calibrated
relevance probabilities. A stronger lexical weight brought citizenship cases
back into birth-control results; semantic evidence now receives more weight.
This improves the checked examples but does not establish general precision or
recall. Related abortion/medical cases can still appear for birth control.
ANES/GSS search, scoring and aggregation are unchanged.

Query encoding runs locally, inference is serialized, recent results are cached
(32 queries), and the vector matrix is memory-mapped. This does not load the
abandoned cross-encoder or the NMF models. Changing the bundle requires restart.

## Validation and limits

55 unit tests passed. Hybrid tests cover independent lexical nomination, the
separate chart filter, cache reuse, semantic-only queries, weak-query abstention
and checksum rejection. Forty-two HTTP requests passed on the local Gunicorn
preview, including concurrent cached requests, birth-control positives/negatives,
Obergefell/Windsor and a nonsense-query empty result. The slowest initial request
was about 0.076 seconds, with cached requests below 0.007 seconds in this run.

The standalone evaluator is `scripts/check_hybrid.py`; it reports candidate and
chart counts separately. Results are still subject to the limitations of the
small development relevance set. Before deployment, review 15–20 representative
queries, reserve some for validation, and run a full VPS serving/load test. The
previous 172 MiB VPS measurement used the same full embedding bundle but an older
candidate rule; it is not a serving measurement for this new implementation.

The old release packager does not include the optional model assets/dependencies.
Do not deploy this mode through that packager without updating and validating it.
