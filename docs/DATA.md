# Raw inputs and reproducible rebuilds

## Historical reproduction is a distinct target

The checked-in codebook describes the historical ANES cumulative file through
2016. Preserve the checked-in SCDB/codebook/labels for a historical reconstruction.
The exact raw release checksums were never recorded, so even recovered files
cannot establish byte-for-byte reproduction of the 2018 run. Record recovered
file hashes and label the resulting artifact honestly.

The current [ANES cumulative page](https://electionstudies.org/data-center/anes-time-series-cumulative-data-file/)
provides a February 5, 2026 STATA archive through 2024, at
<https://electionstudies.org/anes_timeseries_cdf_stata_20260205/>.
ANES explicitly requires the codebook matching its cumulative release. Do not
silently combine it with this repository's old codebook. Prefer recovering the
historical `.dta` or obtaining the historical release from ANES. A newer-data build
requires reviewing/replacing codebook and orientations; `--allow-new-anes` is an
explicit override after that review, not an automatic migration. The default
build rejects observed survey years after 2016. This guard does not prove release
identity: hashes and source records still matter.

SCDB CSV snapshots are already tracked, so they need not be fetched to restore
the app. Fresh snapshots can be obtained from <https://scdb.wustl.edu/> but will
change matching/results and must be versioned separately. Manual orientation
labels are project research inputs, not data that can be redownloaded from ANES.

## Download with a source manifest

`python -m scvpublic.download manifest.json` streams files into `data/raw`, checks
SHA-256 before publishing, and skips existing files only when hashes match. It
requires explicit HTTPS URLs and hashes. A manifest has this structure:

```json
{
  "files": [
    {
      "url": "https://provider.example/snapshot.csv.bz2",
      "path": "snapshot.csv.bz2",
      "sha256": "REPLACE_WITH_64_CHARACTER_LOWERCASE_SHA256"
    }
  ]
}
```

This is a schema example, not a working download manifest. Choose and obtain a
source release once from the official provider, compute `shasum -a 256 FILE`,
and save its URL/hash for subsequent repeatable downloads. No fabricated hashes
or mutable `latest` URLs are shipped. If the provider requires a login, download
through its official interface and hash the local file. Keep the manifest with
your artifact release. Archives are not automatically extracted; inspect ZIP
contents and extract the chosen Stata file to
`data/anes/anes_timeseries_cdf.dta`.

## CourtListener input options

Recovering the old matrix plus its existing row/column CSVs is the fastest route:
`make build` imports it directly. Recovering the old normalized CSV allows fresh
TF-IDF generation. Its required columns are `citation`, `case_name`, `opinion`.
Rows are opinions, not unique cases; retain ordering for tied search scores.

For original per-opinion API JSON files:

```sh
.venv/bin/python -m scvpublic.ingest \
  --json-dir data/scotus_opinions/json \
  --output data/scotus_opinions/scotus_opinions.csv
```

Files are processed in sorted filename order (the old script used filesystem
order). This makes subsequent runs deterministic but can change tied results
relative to the historical matrix. HTML text precedes plain text, as in the old
parser; missing fields no longer leak values from the previous opinion.

For a fresh corpus, consult [CourtListener bulk documentation](https://www.courtlistener.com/help/api/bulk-data/)
and its [snapshot listing](https://com-courtlistener-storage.s3-us-west-2.amazonaws.com/list.html?prefix=bulk-data/).
Choose **one dated snapshot** of `dockets`, `opinion-clusters`, `citations`, and
`opinions`. These contain all courts and the opinion file is particularly large;
download and process on a workstation with sufficient disk space, not a 1 GB VPS.
Input accepts `.csv`, `.csv.gz`, or `.csv.bz2`:

```sh
.venv/bin/python -m scvpublic.ingest \
  --dockets data/raw/dockets-DATE.csv.bz2 \
  --clusters data/raw/opinion-clusters-DATE.csv.bz2 \
  --citations data/raw/citations-DATE.csv.bz2 \
  --opinions data/raw/opinions-DATE.csv.bz2 \
  --output data/scotus_opinions/scotus_opinions.csv
```

The importer joins docket → cluster → opinion on disk, filters court ID `scotus`,
and gets U.S. citations from the citation table. It preserves all matching opinion
rows, including empty text, so corpus document-frequency denominators remain
explicit. It uses text fields from the opinions table; source schema changes or
text moved exclusively into other tables require adapting the importer. The
verified field definitions are in [CourtListener's bulk export script](https://github.com/freelawproject/courtlistener/blob/main/scripts/make_bulk_data.sh).
An adjacent `.sources.json` records input and output hashes. Keep it with the
normalized CSV. The artifact records the CSV hash; together these form provenance.

Then follow the README build command with `--opinions`. A fresh snapshot will not
reproduce the original 64,184-document corpus exactly. Do not claim otherwise.

## Build and inspect

Build-only dependencies include pandas, NumPy, SciPy and sklearn. Both raw text
and TF-IDF fitting can exceed 1 GB; the build is intentionally offline. Serving
needs only Flask/Gunicorn and SQLite. Do not upload raw inputs into the image.

```sh
make inspect
.venv/bin/python -m scvpublic.inspect artifacts/search.sqlite --term government
```

Review source hashes, input versions, Court match coverage and number of
plottable survey questions before publishing. A low match count or few usable
question summaries is a data-quality issue, not a reason to infer missing labels.

## Targeted CourtListener API download (requires adequate rate limits)

A current SCOTUS-only API crawl avoids downloading the all-courts bulk export.
Keep a token in `.courtlistener-token` (one value, no quotes) or set
`COURTLISTENER_TOKEN` in the process environment. The local token file is ignored
by Git and should have mode 600. Never include the token in command arguments,
source manifests, or logs.

```sh
.venv/bin/python -m scvpublic.courtlistener
.venv/bin/python -m scvpublic.courtlistener --status
.venv/bin/python -m scvpublic.courtlistener --usage
```

The first command follows CourtListener's cursor pagination, ordered by ID,
filtered to `scotus`, and selects only needed fields. It downloads clusters
(case metadata/citations) first and opinion text second. It waits between requests
and retries temporary failures while respecting numeric Retry-After headers.
Each page commits records and its next cursor together in
`data/raw/rebuild/courtlistener.sqlite`; rerun the same command to resume.
`--max-pages N` provides a bounded acquisition test. Do not run two downloaders
against the same cache simultaneously.

The tested token has limits of 5 requests/minute, 50/hour and 125/day; observed
pages contain 20 records. This makes a full corpus crawl a multiweek task, not
a quick replacement for bulk acquisition. Check `--usage` before starting a
full crawl. Higher limits require arranging access with Free Law Project; the
downloader does not purchase access. A server-requested wait over 60 seconds
stops the command with the checkpoint intact rather than silently sleeping for
hours. The default spacing avoids the five-per-minute burst limit, but does not
eliminate the hourly or daily limits.

Only completed streams with all opinion-to-cluster joins resolved produce
`data/raw/rebuild/scotus_opinions.csv` plus `.sources.json`. Page response hashes,
retrieval timestamps and public request URLs are kept in the cache. Tokens are
never saved there. An API crawl is not a transactional snapshot: source records
may change during acquisition. Keep the completed cache/CSV and hashes to make
subsequent local builds reproducible. Do not describe it as the historical corpus.

As checked on 2026-10-22, the September 30, 2026 all-courts export had about 59 GiB
of compressed opinions, clusters, dockets and citations. Use the targeted API
when local storage is limited. The downloader exports all returned opinion types;
it does not silently narrow the collection to majority opinions.

## Small real-data smoke test

No full corpus download is needed to exercise the app. To acquire a bounded
sample (at most one page from each API stream in a new cache):

```sh
.venv/bin/python -m scvpublic.courtlistener --sample \
  --date-from 2015-06-22 --date-to 2015-06-26 \
  --cache data/raw/sample/courtlistener.sqlite \
  --output data/raw/sample/scotus_opinions.csv
.venv/bin/python -m scvpublic.sample
make serve ARTIFACT=artifacts/sample.sqlite
```

Sample mode exports only opinions with downloaded cluster metadata; the source
manifest reports any unmatched opinions excluded and marks the corpus partial.
It never marks unfinished API streams complete. The initial test cache may have
more metadata pages from the bounded date-range probe; no further metadata pages
are fetched by `--sample` when that stream already exists.

The sample uses real opinion text, fresh Court TF-IDF, the historical SCDB case
snapshot, and the checked-in ANES question search index. It deliberately leaves
survey trends disabled: the new ANES response data/codebook have been downloaded,
but the historical question orientations and response mappings still need review.
The UI labels this limitation and the sample's actual dates/count. Search rankings
and IDF values depend on the small sample; these are not full-corpus results.

### Parse the fresh ANES release

The downloaded 2026-02-05 archive and matching PDF codebooks are retained in
`data/raw/rebuild/anes-20260205/`; `sources.json` records their hashes.
Run `make anes` to parse the Stata file into `data/processed/anes-20260205/`.
The parser reads 2,000 respondents at a time and requires no network access.
It refuses to overwrite an existing output directory; use
`python -m scvpublic.anes --output PATH` for a separate reproducibility run.

Outputs: `variables.csv` (all short variable descriptions), `value_labels.csv`
(Stata label sets and original numeric codes), `respondents_by_year.csv`,
`response_counts.csv` (unweighted counts for historically classified variables),
`orientation_review.csv` (historical labels, presence in the new file, pending
review), and `manifest.json` (source/output hashes and reconciliation totals).
Counts retain coded missing responses; an empty raw code means system missing.
These are offline intermediate files, not serving artifacts. Short descriptions
are not substitutes for the full question wording in the matching codebook.

Before enabling current public-opinion trends, review the full question wording,
answer scales, missing codes, and historical orientations against the matching
codebook. Do not infer liberal/conservative direction from numeric code order.
No new weighting or scoring methodology is applied by this parser.

The historical CNN (`train_cnn_model.py`) learned Biden/Trump tweet labels.
`classify_questions.py` only runs example phrases. The app used
`data/anes/classified_questions.csv` directly; the notes describe ANES classifier
training/export as unfinished. TensorFlow is unnecessary for parsing or serving.
