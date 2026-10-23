# NMF topic retrieval evaluation

**Conclusion:** NMF learns recognizable broad legal themes, but this experiment
does not justify replacing keyword retrieval. The 50-, 100- and 200-topic models
all struggle to map short topic queries to the intended cases. Flask and the
public service are unchanged.

## Reproduce

Use the existing offline build/CaseSumm dependencies and verified source data:

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 PYTHONPATH=. \
  .venv/bin/python scripts/test_nmf.py --output artifacts/nmf-mu
OPENBLAS_NUM_THREADS=2 PYTHONPATH=. .venv/bin/python \
  scripts/check_nmf_phrases.py artifacts/nmf-mu
```

The training script refuses an existing output folder. The final reports are
`artifacts/nmf-mu/report.json` and `artifacts/nmf-mu/phrase-query-report.json`.
The vectorizer, case metadata, fitted NMF models and normalized case-topic arrays
are saved alongside them. No topic model is loaded by the web application.

## Method

Inputs: 7,734 complete syllabuses and 391 full official-opinion fallbacks,
preserving all 8,125 case IDs. The summary loader verifies source checksums.
The opinion fallbacks can have broader topic mixtures than the shorter summaries;
this is a limitation of the mixed source coverage.

TF-IDF uses English stopwords, unigrams/bigrams, minimum document frequency three,
maximum document frequency 1.0, sublinear term frequency and float32. There is no
vocabulary-size cap: 189,725 features and 2,927,371 nonzero entries. The query
uses the same vocabulary and IDF as training.

NMF uses multiplicative updates with the Frobenius objective, NNDSVDa
initialization, seed 42, tolerance 0.0001 and at most 300 iterations. Each query
is projected with `NMF.transform`, without refitting the topics. Topic coordinates
are multiplied by their corresponding component's L2 norm and then normalized
before cosine comparison. This removes arbitrary reciprocal factor scaling.
These similarities are not probabilities. An out-of-vocabulary query returns
no cases. The diagnostic 20%-of-best count is not an accepted relevance filter.

The secondary phrase experiment uses only the whole query expression when it
exists as a vocabulary feature; otherwise it retains the original features.
It changes neither the fitted model nor any topic-specific rules.

## Results

All three final models converged without warnings:

| Topics | Fit seconds | Iterations | Eight-query projection seconds | Combined topic matrices, MiB |
| --- | ---: | ---: | ---: | ---: |
| 50 | 19.2 | 70 | 0.13 | 37.7 |
| 100 | 45.5 | 80 | 0.39 | 75.5 |
| 200 | 93.8 | 90 | 0.62 | 150.9 |

Matrix sizes exclude Python, vocabulary and library overhead. Peak RSS across
training the three models was approximately 1,432 MiB on the workstation. This
is offline training memory, not a measured serving footprint. No VPS deployment
or HTTP load test was warranted given the relevance results.

At 200 topics:

- Birth control maps strongly to child/paternity and citizenship topics. Nguyen
  and Miller lead the standard-query results. Carey ranks 150, Griswold 274 and
  Eisenstadt 329. Projecting the whole phrase improves these to 7, 34 and 49,
  respectively, but Hobby Lobby remains at 550.
- Contraception maps into a broad abortion/reproductive-health topic. The model
  does not discover the narrow equivalent-expression relationship we need.
- Gay marriage maps largely to spouse/gender and family-status topics. Obergefell
  ranks 57, Windsor 65 and Hollingsworth 615.
- Gun control maps to a real firearms topic but also a corporate-stock topic.
  Heller ranks 36, Abramski 40 and Bruen 176 with standard query projection.
- Abortion has a clear topic and returns substantively related cases such as
  Danforth, Colautti and Akron. It still ranks Roe 16, Casey 17 and Dobbs 32.

This shows two distinct problems: short-query ambiguity and topics broader than
specific policy issues. Whole-phrase projection helps the first, but not enough
to solve the second. More topics do not guarantee the desired policy categories.

Judgments are the existing small development set: 15 relevant and eight irrelevant
query/case pairs over four topics. Unjudged cases are not counted as irrelevant.
In particular, few checked landmarks in the top ten does not mean every returned
case is bad. The reports include actual case lists, leading topic words and
representative cases so results can be inspected beyond the limited labels.
A cosine TF-IDF baseline uses the identical matrix to control preprocessing.

All 54 unit tests passed, including factor-scale invariance, zero-query abstention
and stable tie ordering. The experiment has no effect on survey retrieval or the
running local/public search.

## Diagnostic runs

`artifacts/nmf-evaluation` is an incomplete 20,000-feature-capped run. It dropped
contraception and the birth-control bigram and is excluded from conclusions.
`artifacts/nmf-full-vocabulary` contains completed 50/100-topic coordinate-descent
fits and a stopped 200-topic fit. Profiling identified the coordinate-update loop
as the runtime bottleneck. All three topic counts were rerun consistently with
multiplicative updates in `artifacts/nmf-mu`; these are the final comparison.
