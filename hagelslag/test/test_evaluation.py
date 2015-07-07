__author__ = 'djgagne'

import unittest
from hagelslag.evaluation.ProbabilityMetrics import DistributedReliability, DistributedROC, DistributedCRPS
import numpy as np


class TestProbabilityMetrics(unittest.TestCase):
    def setUp(self):
        self.num_forecasts = 1000
        self.forecasts = dict(perfect=np.concatenate((np.ones(self.num_forecasts/2), np.zeros(self.num_forecasts/2))),
                              random=np.random.random(self.num_forecasts))
        self.observations= dict(perfect=self.forecasts['perfect'],
                                random=self.forecasts['perfect'])
        self.thresholds = np.arange(0, 1.2, 0.1)
        self.obs_threshold = 0.5
        return

    def test_reliability(self):
        perfect_rel = DistributedReliability(self.thresholds, self.obs_threshold)
        perfect_rel.update(self.forecasts["perfect"], self.observations["perfect"])
        random_rel = DistributedReliability(self.thresholds, self.obs_threshold)
        random_rel.update(self.forecasts["random"], self.observations["random"])
        perfect_components = perfect_rel.brier_score_components()
        self.assertEqual(perfect_rel.frequencies["Total_Freq"].sum(), self.num_forecasts,
                         msg="Total Frequency does not match number of forecasts.")
        self.assertEqual(perfect_rel.frequencies["Positive_Freq"].sum(), self.num_forecasts / 2,
                         msg="Positive Frequency does not match number of positive forecasts.")
        self.assertEqual(perfect_components[1], perfect_components[2], "Resolution does not equal uncertainty.")
        self.assertEqual(perfect_rel.brier_score(), 0,
                         msg="Perfect Brier score is {0:0.3f}".format(perfect_rel.brier_score()))
        self.assertGreater(random_rel.brier_score(), perfect_rel.brier_score(),
                           msg="Perfect (BS={0:0.3f}) has worse score than random (BS={1:0.3f})".format(
                               perfect_rel.brier_score(), random_rel.brier_score()))

    def test_roc(self):
        perfect_roc = DistributedROC(self.thresholds, self.obs_threshold)
        perfect_roc.update(self.forecasts["perfect"], self.observations["perfect"])
        perfect_auc = perfect_roc.auc()
        random_roc = DistributedROC(self.thresholds, self.obs_threshold)
        random_roc.update(self.forecasts["random"], self.observations["random"])
        random_auc = random_roc.auc()
        self.assertEqual(perfect_auc, 1, msg="Perfect AUC not 1, is actually {0:0.2f}".format(perfect_auc))
        self.assertAlmostEqual(random_auc, 0.5, places=1,
                               msg="Random AUC not 0.5, actually {0:0.3f}".format(random_auc))
        self.assertGreater(perfect_auc, random_auc, msg="Perfect AUC is not greater than random.")


