# SCOTUS versus public opinion

A rebuilt 2018 Data Incubator capstone: search Supreme Court opinions and ANES
survey questions locally, then compare descriptive liberal/conservative trends.
Flask serves a precomputed SQLite search index; no API or model training runs
on a request.

## Run locally

Python 3.12 is required. With the current locally built artifact:

```sh
make setup
make test
make check-serving
make serve
```

Open http://127.0.0.1:8000/?q1=abortion. The default artifact is
`artifacts/casesumm.sqlite`. For a fresh checkout without downloaded data:

```sh
make setup
make demo
make serve ARTIFACT=artifacts/demo.sqlite
```

Demo data are synthetic. For serving alone, install `requirements.txt`; `make
setup` installs the larger build dependencies including Arrow.

## Rebuild the data

See [CaseSumm acquisition and matching](docs/CASESUMM_REVIEW.md) and
[ANES mappings](docs/ANES_REVIEW.md) for source versions, download instructions,
checksums and exclusions. Raw downloads and generated artifacts are ignored by
Git. Keep the source archives and build manifests for reproducibility.

The current workflow, once those raw sources are present, is:

```sh
make public       # ANES respondents + reviewed response mappings -> public.json
make casesumm     # CaseSumm opinions + SCDB votes + public.json -> SQLite
make inspect
make check-serving
```

CaseSumm refuses to overwrite its index bundle. For another complete build use
`python -m scvpublic.casesumm --bundle artifacts/casesumm-index-v2 --output
artifacts/casesumm-v2.sqlite`. To update only ANES, use `make refresh-public`,
then restart the serving process. Build on a workstation, not the VPS.
`make build` is the historical pipeline and requires its original inputs;
it does not produce the current reviewed ANES methodology.

The current artifact contains 7,018 matched cases from 1950–2016 and 127 ANES
variables in 98 question families. ANES observations extend beyond Court
coverage. Not every ANES variable measures a political attitude; some included
measures are explicitly labeled partisan or movement proxies.

## Methodology

Search sums TF-IDF weights and returns up to ten results per corpus. Phrases
are split into words; public searches also boost adjacent bigrams. This is
partial-word-set matching, not an exact phrase requirement. Very common Court
terms removed during TF-IDF construction may return no Court results.

SCDB direction supplies the sign of the Court score, multiplied by the absolute
vote margin divided by total votes. CaseSumm matches use citations or unique
term/docket identifiers; ambiguous records are excluded. The historical Court
aggregation still keeps the last ranked case for each year. This limitation is
preserved rather than silently changing the original comparison.

ANES response codes have explicit reviewed mappings to [-1, 1], with +1 liberal.
Missing answers are excluded and documented survey weights applied. Retrieved
variants are deduplicated by question family per year; selected comparative
indices supersede their components. Question-family means are equally weighted
in the displayed public series. Trend lines are descriptive linear fits, not
causal estimates or a validated general ideology measure.

## Code layout

- `scvpublic/anes.py`, `public.py`, `casesumm.py`: offline processing and builds.
- `scvpublic/store.py`, `web.py`, `chart.py`: read-only search and Flask serving.
- `scripts/`: source audits, mapping maintenance, release and acceptance tools.
- `deploy/`: systemd and Nginx configuration for `svp.walterslabs.dev`.
- `tests/`: scoring, acquisition, matching, search and request regression tests.

Original root scripts and notebooks are retained as historical references.
The CNN is not used by the rebuilt pipeline.

## Deployment

Run `make release` to check the real artifact and produce an allowlisted bundle.
See [deployment and rollback](docs/DEPLOYMENT.md) for the existing Ubuntu/Nginx
VPS, or the optional Docker route. Only pinned serving dependencies and the
precomputed index are needed at runtime.

Project code uses [LICENSE](LICENSE). Data retain their own terms. CaseSumm's
published license statements conflict; resolve those terms before public
hosting of the derived artifact (details in the CaseSumm review).
