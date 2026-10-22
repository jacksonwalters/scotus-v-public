"""Parse ANES metadata and historical-question counts without ideological recoding."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import tempfile
import os

from .build import digest


def parse(source, labels_path, output, chunk_size=2000):
    import pandas as pd
    if output.exists():
        raise ValueError(f'Output already exists: {output}; choose a new directory')
    if chunk_size < 1:
        raise ValueError('chunk size must be positive')
    labels = {}
    with labels_path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            if row['vcf_code'] and row['ques_class']:
                code = row['vcf_code']
                if code in labels:
                    raise ValueError(f'Duplicate label: {code}')
                value = float(row['ques_class'])
                if value not in (-1, 0, 1):
                    raise ValueError(f'Invalid orientation for {code}')
                labels[code] = int(value)
    with pd.read_stata(source, iterator=True, convert_categoricals=False) as reader:
        variables = reader.variable_labels()
        value_labels = reader.value_labels()
    selected = sorted(set(labels) & set(variables))
    counts, years = Counter(), Counter()
    # Preserve numeric codes, including explicitly coded DK/NA/refusal responses.
    with pd.read_stata(source, chunksize=chunk_size, convert_categoricals=False,
                       columns=sorted(set(selected) | {'VCF0004'})) as reader:
        for frame in reader:
            year = frame['VCF0004']
            if year.isna().any() or (year % 1 != 0).any():
                raise ValueError('Missing or nonintegral survey year')
            years.update({int(k): int(v) for k, v in year.value_counts().items()})
            for code in selected:
                grouped = frame.groupby(['VCF0004', code], dropna=False).size()
                for (yr, answer), count in grouped.items():
                    raw = '' if pd.isna(answer) else format(float(answer), '.15g')
                    counts[(code, int(yr), raw)] += int(count)
    for code in selected:
        if sum(n for (c, _, _), n in counts.items() if c == code) != sum(years.values()):
            raise ValueError(f'Count reconciliation failed for {code}')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        stage = Path(temporary) / 'parsed'
        stage.mkdir()
        def write(name, header, rows):
            with (stage / name).open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(header)
                writer.writerows(rows)
        write('variables.csv', ['code', 'description'], sorted(variables.items()))
        # Stata exposes label-set names separately; retain those names rather than
        # assuming they always equal the associated variable name.
        write('value_labels.csv', ['label_set', 'raw_code', 'label'],
              ((name, format(float(code), '.15g'), label)
               for name, mapping in sorted(value_labels.items())
               for code, label in sorted(mapping.items())))
        write('respondents_by_year.csv', ['year', 'respondents'], sorted(years.items()))
        write('response_counts.csv', ['code', 'year', 'raw_code', 'count'],
              ((*key, count) for key, count in sorted(counts.items())))
        write('orientation_review.csv', ['code', 'historical_orientation', 'present', 'current_description', 'review_status'],
              ((code, value, code in variables, variables.get(code, ''), 'pending')
               for code, value in sorted(labels.items())))
        report = dict(source=str(source.resolve()), source_sha256=digest(source),
                      historical_labels_sha256=digest(labels_path),
                      variables=len(variables), respondents=sum(years.values()),
                      years=sorted(years), historical_labels=len(labels),
                      matched_labels=len(selected), absent_labels=sorted(set(labels)-set(variables)),
                      response_count_rows=len(counts), pandas_version=pd.__version__,
                      notes=['Counts are unweighted and include coded missing responses.',
                             'Empty raw_code means Stata system missing.',
                             'Historical orientations are unreviewed; no polarity scores generated.',
                             'Variable descriptions are short labels, not full question wording.'])
        report['outputs'] = {p.name: digest(p) for p in sorted(stage.iterdir())}
        (stage / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
        os.rename(stage, output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('data/raw/rebuild/anes-20260205/anes_timeseries_cdf_stata_20260205.dta'))
    parser.add_argument('--labels', type=Path, default=Path('data/anes/classified_questions.csv'))
    parser.add_argument('--output', type=Path, default=Path('data/processed/anes-20260205'))
    parser.add_argument('--chunk-size', type=int, default=2000)
    args = parser.parse_args()
    print(json.dumps(parse(args.source, args.labels, args.output, args.chunk_size), indent=2))


if __name__ == '__main__':
    main()
