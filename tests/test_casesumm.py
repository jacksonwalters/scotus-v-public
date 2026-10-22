import unittest
from scvpublic.casesumm import citation_key, resolve, select


def row(**kwargs):
    return dict(dict(caseId='1950-001',usCite='340 U.S. 1',term='1950',docket='1',
        caseName='Test case',dateDecision='10/1/1950',majVotes='6',minVotes='3',decisionDirection='2'),**kwargs)


class CaseSummTests(unittest.TestCase):
    def test_citation_normalization_and_unique_docket(self):
        self.assertEqual(citation_key('340.US.1'),'340 U.S. 1')
        self.assertIsNone(citation_key('340.US.1950_1'))
        doc,error=resolve('340.US.1950_1',{}, {('1950','1'):[row()]})
        self.assertIsNone(error)
        self.assertEqual(doc['cases'][0]['majority_votes'],6)
        self.assertAlmostEqual(doc['cases'][0]['polarity'],1/3)

    def test_ambiguous_cases_and_conflicting_votes_are_excluded(self):
        self.assertEqual(resolve('340.US.1',{'340 U.S. 1':[row(),row(caseId='1950-002')]},{})[1],'ambiguous_case')
        self.assertEqual(resolve('340.US.1',{'340 U.S. 1':[row(),row(majVotes='5')]},{})[1],'conflicting_scdb_rows')

    def test_duplicates_conflicts_and_year_filter(self):
        citations={'340 U.S. 1':[row()]}
        records=[dict(citation='340.US.1',opinion='same text'),dict(citation='340 U.S. 1',opinion='same  text')]
        selected,excluded,stats=select(records,citations,{},1950,2016)
        self.assertEqual(len(selected),1)
        self.assertEqual(stats['identical_duplicates_removed'],1)
        records.append(dict(citation='340.US.1',opinion='different text'))
        self.assertFalse(select(records,citations,{},1950,2016)[0])
        self.assertFalse(select(records[:1],citations,{},1951,2016)[0])
