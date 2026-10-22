"""Compare historical ANES labels with pdftotext -layout output; never approve scores."""
import argparse
import csv
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata
from difflib import SequenceMatcher


def normalize(value):
    value = unicodedata.normalize('NFKC', value).replace('\\n', ' ')
    value = value.translate(str.maketrans({'’': "'", '‘': "'", '–': '-', '—': '-', '“': '"', '”': '"'}))
    value = re.sub(r'-{2,}', '-', value)
    return re.sub(r'\s+', ' ', value).strip().lower()


def blocks(text):
    # Keep physical PDF page references before stripping recurring page headers.
    lines = []
    for page, content in enumerate(text.split('\f'), 1):
        for line in content.splitlines():
            if re.fullmatch(r'\s*(?:\d+\s*(?:VARIABLE DESCRIPTION)?|VARIABLE DESCRIPTION\s*\d+)\s*', line):
                continue
            lines.append((page, line))
    starts = [(i, re.match(r'^\s*(VCF\d{4}[a-z]?)\s+[A-Z0-9]', line))
              for i, (_, line) in enumerate(lines)]
    starts = [(i, m.group(1)) for i, m in starts if m]
    result = {}
    for n, (i, code) in enumerate(starts):
        end = starts[n+1][0] if n+1 < len(starts) else len(lines)
        body = '\n'.join(line for _, line in lines[i:end])
        matches = list(re.finditer(r'^[ \t]{0,2}(Question|Valid|Missing|Notes|Weight|Sources)[ \t]+', body, re.M))
        if not matches or matches[0].group(1) != 'Question':
            continue
        fields = {}
        for j, m in enumerate(matches):
            fields.setdefault(m.group(1), body[m.end():matches[j+1].start() if j+1 < len(matches) else len(body)].strip())
            if m.group(1) == 'Sources':
                break
        if code in result:
            raise ValueError(f'Duplicate parsed block {code}')
        result[code] = (lines[i][0], fields)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('text', type=Path)
    parser.add_argument('--output', type=Path, default=Path('data/processed/anes-20260205/audit'))
    args = parser.parse_args()
    current = blocks(args.text.read_text())
    with open('data/anes/codebook/formatted_anes_codebook.csv') as f:
        old = {r['vcf_code']: r for r in csv.DictReader(f) if r['vcf_code']}
    with open('data/anes/classified_questions.csv') as f:
        labels = [r for r in csv.DictReader(f) if r['vcf_code'] and r['ques_class']]
    rows = []
    for label in labels:
        code = label['vcf_code']; historical = old[code]
        if code not in current:
            raise ValueError(f'No current Question block for {code}')
        page, fields = current[code]
        title = historical['code_category']
        orientation = int(float(label['ques_class']))
        flags = []
        if orientation == 0:
            flags.append('neutral_or_undecidable_not_evidence_of_centrist_opinion')
        if re.search(r'Mention \d:', title):
            flags.append('nominal_topic_codes_not_ordinal')
        elif code in ('VCF0127a', 'VCF0127b', 'VCF0302'):
            flags.append('nominal_categories_require_explicit_mapping')
        elif 'Thermometer' in title:
            flags.append('thermometer_requires_numeric_scale_and_missing_exclusion')
        elif re.fullmatch(r'VCF03(?:5[0-7]|6[2-9])', code):
            flags.append('candidate_trait_lower_code_more_favorable_reverse_scale')
        elif code in ('VCF0127', 'VCF0374', 'VCF0475', 'VCF0481', 'VCF0487', 'VCF0493'):
            flags.append('yes_lower_than_no_reverse_scale')
        else:
            flags.append('explicit_response_mapping_required')
        if fields.get('Missing'):
            flags.append('exclude_documented_missing_codes')
        row = dict(code=code, historical_orientation=orientation, title=title,
                   pdf_page=page, review_status='blocked_pending_explicit_mapping', flags=';'.join(flags))
        for old_key, key in [('question', 'Question'), ('valid_codes', 'Valid'), ('missing_codes', 'Missing')]:
            a, b = historical[old_key], fields.get(key, '')
            row['old_'+old_key] = a.replace('\\n', '\n')
            row['current_'+old_key] = b
            row[old_key+'_normalized_equal'] = normalize(a) == normalize(b)
            row[old_key+'_text_similarity'] = round(SequenceMatcher(None, normalize(a), normalize(b), autojunk=False).ratio(), 3)
        rows.append(row)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / 'question_audit.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary = dict(reviewed_codes=len(rows), parsed_codebook_blocks=len(current),
                   exact_normalized_matches={key: sum(r[key+'_normalized_equal'] for r in rows)
                                             for key in ['question','valid_codes','missing_codes']},
                   flags=dict(Counter(flag for r in rows for flag in r['flags'].split(';'))),
                   caveat='Text comparison is mechanical, not semantic approval. PDF line wraps and headings can affect equality. All scoring remains blocked.')
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
