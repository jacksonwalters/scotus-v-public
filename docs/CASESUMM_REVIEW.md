# CaseSumm feasibility review

Recommendation: a practical starting corpus for the historical local TF-IDF
rebuild, with coverage/cleaning limitations. It is not a verified complete SCOTUS
archive. No serving artifacts have been replaced by this investigation.

## Acquisition and reproducibility

Downloaded both original Arrow files from ChicagoHAI/CaseSumm revision
`880acec67a69766075ddb42882de4722efdeddb2`:

- `data-00000-of-00002.arrow`: 242,602,720 bytes
- `data-00001-of-00002.arrow`: 261,069,000 bytes

Total: 503,671,720 bytes, approximately 480 MiB. Downloaded in under a minute on
this connection. Files and SHA-256 hashes are retained under `data/raw/casesumm/`.
Install `requirements-casesumm.txt`, then run
`.venv/bin/python scripts/audit_casesumm.py` to reproduce the audit.

Source: https://huggingface.co/datasets/ChicagoHAI/CaseSumm/tree/880acec67a69766075ddb42882de4722efdeddb2
Paper: https://arxiv.org/html/2501.00097v1

## Actual file contents

27,071 rows, containing only citation, syllabus and opinion strings. 26,960
distinct raw citation identifiers; 111 repeated-identifier rows. 470 identifiers
use a volume plus term/docket form rather than a conventional reporter citation.
There are 221 repeated-text rows, one empty opinion, and 830 opinions under 100
whitespace-separated words. Short text is a screening flag, not proof of damage:
some decisions are legitimately brief. Median opinion length is 2,069 words.

The paper describes extraction of majority opinions, with concurrences/dissents
removed. Spot checks locate Roe, Casey, Brown and Heller; Casey's opinion field
begins with syllabus-like text, demonstrating that extraction boundaries still
need checks. No independent completeness audit of every text has been performed.
The paper's 25.6K count differs from the released files' 27,071 rows. Coverage is
advertised as 1815–2019, but the paper also references volume 591 and Trump v.
Vance. Do not assume that advertised years are exact calendar-year boundaries.

## Matching our SCDB snapshot

For decision years 1950–2016, the local SCDB contains 8,334 distinct case IDs.
An exact normalized reporter-citation join, supplemented by term+docket matches
that resolve to one distinct case ID, connects 7,372 (88.5%). This is preliminary
identifier coverage; text identity, duplicate conflicts, vote usability and any
multiple issue/vote rows need validation before publishing a scored artifact.

Among the 7,958 distinct nonempty reporter citations in that period, 7,121
(89.5%) appear in CaseSumm; 6,886 have at least one text of 100 words. These are
different denominators, not conflicting coverage estimates. The local SCDB
snapshot lacks reporter citations for some recent cases (including Obergefell),
so citation-only matching understates usable coverage. Unmatched cases may reflect
source gaps, identifier conventions, or SCDB coverage—not necessarily missing text.
A newer SCDB release may improve matching. Results cannot establish completeness
through 2019 because the local SCDB snapshot does not cover that whole period.

Detailed outputs: `data/raw/casesumm/audit.json` and `coverage_by_year.csv`.
The yearly CSV is citation-only; aggregate case-ID matching additionally uses
unique term/docket identifiers.

## License ambiguity

The publisher's README declares CC BY-NC 3.0 in metadata, CC BY-NC 4.0 in the
summary, and CC BY-NC-SA 4.0 in its license section. These are inconsistent.
The paper is another noncommercial-license statement. Record attribution and
resolve the applicable terms before redistribution/public deployment; this
review does not infer rights for the assembled dataset from the status of the
underlying judicial opinions. Local feasibility testing does not settle licensing.

## Integration plan

Keep opinion text local, normalize identifiers, resolve duplicates, join SCDB
without ambiguous name-only matching, and filter to the desired date range.
Build sparse float32 TF-IDF offline and export the existing disk-backed serving
index. Retain citations, vocabulary, and row mapping together. Full texts and the
matrix need not reside in Flask RAM. Later obtain only verified gaps/newer cases.
No 59 GiB all-courts export is needed to begin this route.

`python scripts/benchmark_casesumm.py` performs a standalone capacity experiment:
selects the longest text per raw identifier with >=100 words, applies the legacy
unigram/English-stopword/min_df/max_df settings with float32, and writes
`benchmark.json` plus an experimental matrix. This is not a deployable artifact
or a claim that longest-text duplicate resolution is analytically correct.

Measured benchmark: 26,135 selected documents × 171,817 terms, 12,238,454 nonzeros.
CSR arrays occupy 98,012,176 bytes (93.5 MiB), compressed NPZ 70,303,841 bytes
(67.0 MiB). Vectorization plus save took 23.28 seconds. Peak process memory was
1,809,694,720 bytes (1.69 GiB) on macOS, including loaded opinion text. Therefore
build on the workstation, not a 1 GiB VPS. This measurement is not a serving RAM
benchmark; the existing serving index is disk-backed.

## Local application integration

Implemented `scvpublic.casesumm` with checksum verification of the pinned Arrow
files. Reproduce from the repository root:

```sh
.venv/bin/python -m pip install -r requirements-casesumm.txt
.venv/bin/python -m scvpublic.download data/manifests/casesumm.json
make public
make casesumm
make serve ARTIFACT=artifacts/casesumm.sqlite
```

`make casesumm` requires a new bundle directory so matrix/mapping files cannot be
silently mixed with an earlier build. For a subsequent build, pass a new
`--bundle` path to `python -m scvpublic.casesumm`. The SQLite serving artifact is
published atomically after integrity checking.

Result: 7,018 cases (6,783 citation matches, 235 unique term/docket matches),
97,872 terms, 32,333,828 bytes in sparse arrays, approximately 22 MiB compressed
matrix and 134 MiB serving database. Bundle at `artifacts/casesumm-index/` contains
matrix, vocabulary, row/case metadata, exclusion report, source hashes and file
hashes. The SQLite artifact also contains the 65 mapped public questions.

Matching is stricter than the feasibility audit: reject identifiers spanning
multiple case IDs, unusable scores, and multiple SCDB rows disagreeing on date,
vote counts or polarity. Exact whitespace-normalized duplicate text is collapsed;
conflicting text for a case is excluded rather than choosing the longest. 230
short nonempty opinions are retained and flagged: length alone is not proof of
bad extraction. No name-only fallback is used. Scored rows include vote counts.

All matched case years are checked to be within 1950–2016. Real-data smoke checks
find Roe and Doe for abortion and Obergefell for marriage. Original TF-IDF
max_df=.30 remains: very common terms such as civil and rights are absent from
the Court vocabulary; more specific words such as discrimination work. Public
coverage and Court coverage differ, and the UI identifies this explicitly. Court
series aggregation still retains legacy last-ranked-case-per-year behavior.

The local server is running at http://127.0.0.1:8003/ using the new artifact.
No dataset was deployed or redistributed publicly. The CaseSumm attribution and
license ambiguity above still apply.
