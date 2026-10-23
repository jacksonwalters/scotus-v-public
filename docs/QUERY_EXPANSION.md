# Query expansion experiment

Status: evaluation only; Flask and the public service continue using baseline
TF-IDF. This candidate improves some precision checks but fails coverage checks.

## Approach

1. Build a general vocabulary from WordNet 3.0 noun, adjective and verb lemmas
   appearing in the verified Court summary sources (including simple plurals).
2. Precompute embeddings for these 26,018 expressions with the pinned MiniLM
   query encoder. At query time, accept up to three neighbors with cosine >= .78.
3. Require a whole expression or its simple appended-s plural to occur in the
   summary, using SQLite FTS5 with unicode61 tokenization. Never let one word of
   a multiword expression bypass the eligibility check.
4. Rank eligible cases with the existing summary TF-IDF scores: original
   expression weight 1, expansion weight .5. Take the maximum contribution per
   case, so multiple near-duplicate synonyms do not multiply a case's score.

There is no case-specific blacklist, topic alias list, case embedding matrix or
candidate reranker. Surveys are unchanged. Source coverage remains 7,734 full
syllabuses and 391 full-opinion fallbacks. Hyphens are normalized as word
boundaries. Morphology is deliberately limited; it is not a general lemmatizer.

**Neighbors are suggestions, not verified synonyms.** The dictionary limits the
vocabulary but does not prove equivalence. For example, abortionist and health
care provider can pass the similarity threshold despite not being equivalent to
abortion and health care. The .78 threshold was adjusted during development
(.80 missed same sex marriage); these checks are not an independent validation.

## Reproduce

Install offline summary/build dependencies and `requirements-expansion.txt`.
Keep the verified raw CaseSumm, SCDB and official supplement used by
`scvpublic.summary`. Download the pinned encoder with:

```sh
PYTHONPATH=. .venv/bin/python scripts/download_query_model.py
curl -fL https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip \
  -o data/raw/wordnet.zip
# If not already built:
.venv/bin/python -m scvpublic.summary
OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false PYTHONPATH=. \
  .venv/bin/python scripts/build_expansion.py
OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false PYTHONPATH=. \
  .venv/bin/python scripts/check_expansion.py
```

The builder checks the dictionary hash in `data/manifests/wordnet.json`, verifies
source hashes through the summary loader, and refuses an existing output folder.
The runtime validates bundle hashes. The WordNet license is copied into the
bundle and must accompany redistribution. WordNet's concept groups are described
at https://wordnet.princeton.edu/ and its license at
https://wordnet.princeton.edu/license-and-commercial-use .

Output: `artifacts/query-expansion/`; evaluation with expansions, full case lists,
known-case ranks, timings and peak RSS: `artifacts/expansion-evaluation.json`.
The generated artifact uses about 185 MiB peak process RSS locally. It has not
undergone a VPS service/load test and is not packaged for deployment.

## Findings

- Birth control -> contraceptive: 13 cases; all six checked relevant cases are in
  the first ten, and none of the four checked false positives remain. Other
  returned cases are unjudged; this is not perfect precision.
- Gay marriage -> same sex marriage: seven cases; Obergefell and Windsor are
  recovered, but Hollingsworth is absent.
- Gun control: no expansion clears the threshold; 11 phrase matches, missing
  Heller, Bruen and Abramski. Exact expression matching is too restrictive here.
- Abortion: the three checked landmark cases appear in the first ten.
- Civil rights: 378 expression matches, demonstrating that a phrase mention can
  still be incidental; no claim is made that all should enter a trend.

All eight previously labeled irrelevant query/case pairs are excluded, but only
11 of 15 labeled relevant cases are retained. This small development set is not
an exhaustive benchmark. There is no automatic deployment or preview switch.

## Cleanup

Removed the unused case-embedding, hybrid fusion and cross-encoder implementations,
build/benchmark scripts, tests and optional Flask semantic route from active code.
The shared small encoder now lives in `scvpublic/encoding.py`. Recoverable source
and prior experiment notes are in `artifacts/retired-search-experiments.tar.gz`.
Raw data, baseline TF-IDF artifacts, generated historical vectors and evaluation
results were preserved. The first expansion bundle is retained separately as
`artifacts/retired-query-expansion-v1/`.
