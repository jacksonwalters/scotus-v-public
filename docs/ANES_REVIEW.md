# ANES compatibility and scoring review

Reviewed 2026-10-22 against the 2026-02-05 ANES cumulative variable codebook.

## Result

All 192 historically labeled variable codes exist in the fresh data. All 192
valid-answer definitions match the historical CSV after normalizing whitespace,
Unicode typography and doubled dashes. Question text matches for 171; missing-code
text matches for 171. These are mechanical comparisons, not certification that
all years or political interpretations are interchangeable.

The 21 question-text differences consist of one bracket correction (VCF0301),
14 historical question fields contaminated by INAP/missing instructions, and six
Democratic-candidate dislike follow-ups changed from “liked” to “didn't like.”
The 21 missing-text differences consist of 16 formerly empty fields and five
added refusal descriptions. Differences may reflect historical extraction errors
or documentation changes; the old source PDF is not available for attribution.

The saved labels end at VCF0498d. Later policy-question variables have no saved
orientation. This looks like partial manual annotation, not a completed classifier
output. Presence of an old code also does not imply observations in 2024.

## Scoring findings

The old Flask `resp_convert` interpolates category *positions* across [-1, 1],
then multiplies by the stored orientation. It does not exclude labeled missing
codes. Reproducing that function on the fresh Stata categories gives:

| Variable | Historical orientation | Answer | Legacy score |
| --- | --- | --- | --- |
| VCF0127 union household | +1 | Yes | 0 |
| VCF0127 union household | +1 | No | +1 |
| VCF0127 union household | +1 | DK/NA | -1 |
| VCF0374 likes Democratic Party | +1 | Yes | -1 |
| VCF0374 likes Democratic Party | +1 | RF/NA | +1 |
| VCF0350 Democratic candidate intelligent | +1 | Extremely well | -1 |
| VCF0350 Democratic candidate intelligent | +1 | NA | +1 |

This is a pre-existing scoring problem, not a newly reversed ANES scale.

Across the 192 entries:

- 80 are nominal candidate-response topic codes: code numbers identify subjects,
  not increasing ideological strength. Do not interpolate them.
- 3 other variables contain nominal categories requiring explicit mapping.
- 55 are thermometer variables needing numeric-scale handling and exclusion of
  missing codes; the historical political orientations remain assumptions.
- 6 binary questions code yes below no; increasing-code scaling conflicts with
  their affirmative-answer orientations.
- 16 candidate-trait variables code favorable answers below unfavorable answers.
- 32 remaining entries require an explicit response interpretation.

These categories sum to 192. Separately, 24 have orientation zero, documented as
“neutral/undecidable.” That is not evidence that respondents hold centrist views;
including these as zeros can dilute an aggregate. All 192 document missing or
inapplicable responses, which need exclusion before aggregation.

## Decision

Keep the historical files and legacy behavior as references. Do not enable new
public trends using the old positional conversion. The sample app remains
unchanged with public trends disabled.

The next implementation should use a versioned, explicit answer-to-score mapping
for a defensible subset, exclude missing/unscorable answers and nominal topic
codes, and keep original orientations visible for review. Separate any survey
weighting change from this correction. A CNN is unnecessary for these mappings
and would not fix response-code semantics.

## Reproduce the comparison

Use Poppler's `pdftotext` (available in the bundled runtime here):

```sh
pdftotext -layout data/raw/rebuild/anes-20260205/anes_timeseries_cdf_codebook_var_20260205.pdf /tmp/anes-codebook.txt
.venv/bin/python scripts/audit_anes.py /tmp/anes-codebook.txt
```

The generated `data/processed/anes-20260205/audit/question_audit.csv` contains all
192 old/current question, valid-code and missing-code definitions, physical PDF
page references, similarity checks, and scoring flags. `summary.json` contains
counts. It is an audit artifact, not an approved scoring manifest. Representative
PDF pages were checked against extracted text; general question introductions
must not overwrite variable-specific text.

## Implemented correction: explicit-anes-v1

The corrected sample build now enables 65 reviewed mappings (59 policy/self-placement
variables plus 6 explicitly partisan/ideological thermometers). This is a first
supported set, not complete classification of all 1,030 variables. Other entries
remain excluded; see `data/anes/mapping_coverage.csv`. Historical labels are intact.

`data/anes/response_mappings.json` records every accepted numeric answer and score,
question text, liberal/conservative rationale, PDF page, missing-code definition,
full-sample weight variable, and alternate-question family. The mapping generator
is `scripts/build_anes_mappings.py`; it requires the matching pdftotext output.
Ideological directions are interpretive project conventions, not ANES labels.

Valid numeric answers are linearly scaled using their documented endpoints, then
oriented liberal-positive. DK/NA/refusal and any unmapped code are excluded even
when the codebook lists them under Valid. Uncertain midpoint code 3 in VCF0818 is
excluded. Thermometer 50 is zero; code 97 (97–100 top-coded) is approximated as 100.
Equal numeric spacing for ordinal answers is an explicit exploratory assumption.
Unchanged gun/immigration/spending policy is a scale midpoint, not an assertion
that the prevailing policy is objectively centrist.

Each question-year mean uses its codebook-listed z full-sample weight (including
VCF0010z/VCF0011z where required). Nonpositive/missing weights are excluded. This
is a deliberate correction from the unweighted legacy means; no standard errors
are estimated. Among retrieved variants in a family, the highest-priority variant
with responses that year is selected, with deterministic code tie-breaking. Family
means then receive equal weight. Search still returns up to ten TF-IDF matches;
changing available questions can change topic composition over time. Only mapped
questions enter this corrected public index, using title plus question text.

Run `make public-sample` to build weighted ANES summaries and
`artifacts/sample-public.sqlite` alongside the untouched historical sample.
Serve with `make serve ARTIFACT=artifacts/sample-public.sqlite`. No model runs on the server.
The artifact contains 20 sampled Court opinions and 65 plottable ANES questions;
its small Court sample cannot support a representative Court time trend.

Verified with endpoint/direction, irregular numeric code, missing-answer,
weighted-mean, and alternate-version deduplication tests, plus real-data searches
for gun, abortion, insurance, immigrants, environmental, and homosexuals. Exact
vocabulary search remains unchanged: for example use “immigrants,” not “immigration.”

### Expanded public index

The active CaseSumm artifact now contains 73 mapped variables in 58 question
families. Added VCF9046/9047/9049/9050 (food stamps, environment, Social Security,
assistance to Black Americans), VCF9131 (government role), VCF9232/9233 (torture),
and VCF9237 (death-penalty strength). Torture and death-penalty strength variants
share a family with their corresponding base question. Spending code 7 (eliminate
entirely) explicitly maps to -1, as does code 3 (decrease); code 2 remains zero.
These are project ideological conventions, not labels supplied by ANES.

Perceptions of government/candidate positions, demographics, general performance
ratings, and cross-cutting trade/outsourcing questions remain excluded. Increasing
the number of variables is not grounds to force an unclear ideological mapping.

After changing mappings, regenerate and publish public data without rebuilding
Court TF-IDF:

```sh
.venv/bin/python scripts/build_anes_mappings.py /tmp/anes-codebook.txt
make public
.venv/bin/python -m scvpublic.refresh_public
```

The refresh replaces the SQLite file atomically and preserves Court rows/postings.
Requests open the artifact afresh, so existing local servers receive the updated
search data. App-level metadata loaded at startup refreshes on restart.

## Complete inventory eligibility pass

All 1,030 variables now have a disposition in `data/anes/mapping_coverage.csv`;
summary counts are in `data/anes/inventory_review.json`. This pass reviewed the
full variable inventory by measurement type and examined the codebook question,
response scale and weight for newly accepted candidates. It is not a claim that
all 1,030 full codebook entries received an independent historical validity audit.
Exclusions are scoped to a fixed liberal/conservative topic score, not claims that
those variables have no research value or could never be used with more context.

Current result: 92 mapped variables in 70 question families (19 variables and
12 families added). New direct content includes school prayer, unequal chances
in life, federal government power, government/free-market economic management,
and explanations of government growth. Left/right self-placement joins the
existing self-ideology family. Party identification and explicitly partisan
candidate feeling ratings are accepted as **partisan proxies**, not direct issue
preferences. Their rationales state this limitation. CSES 0–10 feeling ratings
share families with the corresponding thermometers; preferred variants prevent
double-counting when retrieved together. Party ID uses the seven-point summary
in preference to its three-category version. Unmapped initial nominal party-ID
responses are not interpolated. School-prayer strength alone is excluded because
it supplies no direction; the parent question is included.

Largest exclusion groups: 204 nominal open-ended topic codes; 106 election/contact
administration variables; 98 personal characteristics; 87 electoral behaviors;
84 perceived positions of others; 78 ambiguous thermometer/affect measures;
54 trust/efficacy/participation measures; 44 candidate-trait assessments. Remaining
categories and their per-variable reasons are available in the inventory. No
variable is left with the old generic “pending interpretation” placeholder.

VCF0906 and VCF0907 are withheld because the codebook flags pending corrections
for 2016 House candidate thermometers. Foreign policy/trade/outsourcing, religious
identity and child-rearing proxies, and institutional trust were not forced into
a universal historical left/right ordering. Policy-independent candidate traits
and named-person ratings require additional context before inclusion. Derived
indices were not added alongside their source measures, avoiding duplication.

Reproduce the dispositions with `python scripts/review_anes_inventory.py`.
The mapping generator also runs it after generating new mappings. Tests verify
complete inventory coverage, synchronization with the accepted maps, school-prayer
and CSES scale direction, exclusions, weights and variant deduplication.

## Expanded proxy and derived-index coverage

The active artifact now uses 127 variables assigned to 98 families. This adds
24 explicitly partisan positive candidate-trait scales, seven movement/economic-
group thermometers, and four comparative thermometer indices to the previous 92.
The family count includes four derived families that replace component families
when retrieved together; it is not 98 independent survey constructs.

Candidate traits are proxies: favorable Democratic assessments score positive,
favorable Republican assessments negative. This is an interpretive extension,
not evidence that perceived honesty/intelligence is itself a policy preference.
The UI labels partisan and movement proxies. The historical project's directions
are reused for business, labor unions, civil-rights leaders, women's movement,
environmentalists, anti-abortion activists and feminists. Feelings toward these
groups need not match policy views; they broaden exploratory coverage at that cost.

Four-point and five-point versions of leadership/care/knowledge share families.
Women's-movement and feminist thermometers share a family. Comparative party,
presidential-candidate, VP-candidate, and liberal/conservative indices suppress
retrieved source measures for each year the derived index is available. No source
is suppressed for years lacking that index. Code 50 remains neutral in comparative
party/candidate indices; code 49 remains neutral in VCF0801, with piecewise scaling
to preserve the documented endpoints. Original rounding/top-coding cannot be
undone. Index values are not rescaled using observed sample extrema.

Remaining boundaries are substantive, not unfinished automatic classification:
nominal response topics, identity/demographics, perceived positions of other
actors, political attention and generic institutional performance do not directly
answer the ideological preference question. Likes-minus-dislikes counts inherit
source zero codes merging no mentions and DK/NA (e.g. VCF0315); they cannot recover
clean substantive answers. Candidate emotion flags include 1980 DK merged with
'no' and do not establish an opposite stance when an emotion is absent. The House
thermometer index inherits the source correction issue. These require additional
source data or different assumptions before defensible use. Period-dependent
foreign-policy/trade questions remain unscored rather than assigned an invariant
sign. Thus this is broader usable coverage, not proof that every conceivable
interpretation of the remaining data is exhausted.
