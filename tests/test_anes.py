import csv
from pathlib import Path
import tempfile
import unittest

import pandas as pd
from scvpublic.anes import parse


class AnesTests(unittest.TestCase):
    def test_chunked_counts_preserve_missing_and_orientation_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, labels = root / 'input.dta', root / 'labels.csv'
            pd.DataFrame({'VCF0004': [2000, 2000, 2004, 2004],
                          'VCFTEST': [1., 9., float('nan'), 1.]}).to_stata(
                source, write_index=False, variable_labels={'VCFTEST': 'Test question'},
                value_labels={'VCFTEST': {1: 'Yes', 9: 'Refused'}})
            labels.write_text('vcf_code,ques_class\nVCFTEST,-1\nVCFGONE,1\n')
            result = parse(source, labels, root / 'out', chunk_size=1)
            self.assertEqual(result['respondents'], 4)
            self.assertEqual(result['absent_labels'], ['VCFGONE'])
            with (root / 'out/response_counts.csv').open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(sum(int(r['count']) for r in rows), 4)
            self.assertEqual({r['raw_code'] for r in rows}, {'1', '9', ''})
            self.assertIn('pending', (root / 'out/orientation_review.csv').read_text())
            with self.assertRaises(ValueError):
                parse(source, labels, root / 'out')
