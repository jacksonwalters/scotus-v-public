from collections import defaultdict
import json
from pathlib import Path
import unittest
import pandas as pd
from scvpublic.public import aggregate, validate
from scvpublic.store import series

class PublicTests(unittest.TestCase):
    def setUp(self):
        self.mapping=json.loads(Path('data/anes/response_mappings.json').read_text())
        self.entries={e['code']:e for e in self.mapping['entries']}

    def test_endpoints_and_numeric_not_position_scaling(self):
        validate(self.mapping)
        gun=self.entries['VCF9238']['scores']
        self.assertEqual(gun,{'1':1.,'2':0.,'3':-1.})
        self.assertEqual(self.entries['VCF0838']['scores']['4'],1.)
        self.assertEqual(self.entries['VCF0806']['scores']['1'],1.)
        self.assertEqual(self.entries['VCF0218']['scores']['50'],0.)
        self.assertAlmostEqual(self.entries['VCF0218']['scores']['75'],.5)
        self.assertNotIn('98',self.entries['VCF0218']['scores'])
        self.assertNotIn('3',self.entries['VCF0818']['scores'])

    def test_expanded_policy_mappings(self):
        for code in ['VCF9046','VCF9047','VCF9049','VCF9050']:
            self.assertEqual(self.entries[code]['scores'], {'1':1.,'2':0.,'3':-1.,'7':-1})
        self.assertEqual(self.entries['VCF9233']['scores']['7'],1.)
        self.assertEqual(self.entries['VCF9233']['family'],self.entries['VCF9232']['family'])
        self.assertEqual(self.entries['VCF9237']['family'],self.entries['VCF9236']['family'])
        self.assertGreater(self.entries['VCF9237']['priority'],self.entries['VCF9236']['priority'])

    def test_weighted_average_missing_and_zero_weight(self):
        entry=self.entries['VCF9238']; totals=defaultdict(lambda:[0.,0.,0])
        frame=pd.DataFrame({'VCF0004':[2000]*6, 'VCF9238':[1,3,-8,-9,1,1],
                            entry['weight']:[3,1,100,100,0,float('nan')]})
        aggregate(frame.iloc[:2], [entry], totals)
        aggregate(frame.iloc[2:], [entry], totals)
        total=totals[('VCF9238',2000)]
        self.assertEqual(total,[2.,4.,2])
        self.assertEqual(total[0]/total[1],.5)

    def test_family_deduplication_and_available_year_fallback(self):
        docs=[dict(code='A',family='f',priority=0,years={'2000':-1,'2004':1}),
              dict(code='B',family='f',priority=10,years={'2000':1}),
              dict(code='C',family='g',priority=0,years={'2000':0})]
        self.assertEqual(series([],docs)[1],{2000:.5,2004:1})

    def test_full_inventory_has_disposition_and_mapping_consistency(self):
        import csv
        with open('data/anes/mapping_coverage.csv') as stream:
            rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),1030)
        self.assertEqual(len({r['code'] for r in rows}),1030)
        self.assertEqual({r['code'] for r in rows if r['status']=='mapped'},set(self.entries))
        self.assertTrue(all(r['reason'] for r in rows))
        self.assertNotIn('VCF9043a',self.entries)
        self.assertNotIn('VCF0907',self.entries)
        self.assertEqual(self.entries['VCF9043']['scores']['1'],1)
        self.assertEqual(self.entries['VCF9051']['scores']['5'],1)
        self.assertEqual(self.entries['VCF9240']['scores']['5'],0)
        self.assertEqual(self.entries['VCF9202']['scores']['10'],-1)

    def test_expanded_proxies_and_index_midpoints(self):
        self.assertEqual(self.entries['VCF0350']['scores']['1'],1)
        self.assertEqual(self.entries['VCF0362']['scores']['1'],-1)
        self.assertEqual(self.entries['VCF9209']['family'],self.entries['VCF0356']['family'])
        self.assertEqual(self.entries['VCF0230']['scores']['97'],-1)
        self.assertEqual(self.entries['VCF0291']['scores']['50'],0)
        self.assertEqual(self.entries['VCF0801']['scores']['49'],0)
        self.assertEqual(self.entries['VCF0801']['scores']['97'],-1)

    def test_derived_index_suppresses_only_available_year_components(self):
        docs=[dict(code='A',family='a',years={'2000':1,'2004':1}),
              dict(code='B',family='b',years={'2000':1}),
              dict(code='INDEX',family='index',supersedes=['A','B'],years={'2000':0})]
        self.assertEqual(series([],docs)[1],{2000:0,2004:1})
