import unittest
import numpy as np
from scvpublic.topics import topic_coordinates,ranked_cases


class TopicTests(unittest.TestCase):
    def test_factor_scaling_does_not_change_retrieval_coordinates(self):
        weights=np.array([[1.,2.],[0.,0.],[2.,1.]])
        components=np.array([[3.,0.,1.],[0.,2.,2.]])
        scale=np.array([.1,8.])
        actual=topic_coordinates(weights,components)
        np.testing.assert_allclose(actual,topic_coordinates(weights*scale,components/scale[:,None]))
        np.testing.assert_array_equal(actual[1],[0.,0.])
        np.testing.assert_allclose(np.linalg.norm(actual[[0,2]],axis=1),[1.,1.])

    def test_zero_query_yields_no_cases_and_ties_are_stable(self):
        docs=[{'case_id':'a'},{'case_id':'b'},{'case_id':'c'}]
        self.assertEqual(ranked_cases(np.zeros(3),docs),[])
        self.assertEqual([h['case_id'] for h in ranked_cases(np.array([.5,.5,.1]),docs)],['a','b','c'])
