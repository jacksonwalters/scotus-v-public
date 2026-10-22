import unittest
from scripts.audit_anes import blocks, normalize


class AuditTests(unittest.TestCase):
    def test_wrapped_numeric_heading_pages_and_general_introduction(self):
        text = '''VCF0303 3-CATEGORY
Question   Original question
Valid      1. First
\f114             VARIABLE DESCRIPTION
           2. Second
Missing    9. NA
Sources    2024: example
Question   Unrelated general introduction
VCF0350 CANDIDATE
Question   Next question
Valid      1. Extremely well
Missing    9. NA
'''
        result = blocks(text)
        self.assertEqual(result['VCF0303'][1]['Question'], 'Original question')
        self.assertNotIn('VARIABLE DESCRIPTION', result['VCF0303'][1]['Valid'])
        self.assertIn('2. Second', result['VCF0303'][1]['Valid'])
        self.assertEqual(result['VCF0350'][0], 2)

    def test_typography_normalization(self):
        self.assertEqual(normalize('Democrats -- feeling\\nthermometer'),
                         normalize('Democrats – feeling thermometer'))
