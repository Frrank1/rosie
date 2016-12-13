from unittest import TestCase, main, skip
from unittest.mock import MagicMock, patch
from rosie.meal_price_outlier_classifier import MealPriceOutlierClassifier
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import sklearn


class TestMealPriceOutlierClassifier(TestCase):

    def setUp(self):
        self.dataset = pd.read_csv('tests/meal_price_outlier_classifier.csv',
                                   dtype={'cnpj_cpf': np.str})
        self.subject = MealPriceOutlierClassifier()
        self.subject.fit(self.dataset)

    @patch('rosie.meal_price_outlier_classifier.KMeans')
    def test_predict_returns_a_prediction_for_each_observation(self, kmeans_mock):
        kmeans_mock.return_value.predict.return_value = np.ones(3)
        self.subject.fit(self.dataset)
        self.assertTrue(kmeans_mock.return_value.fit.called)

    def test_predict_outlier_for_common_cnpjs_when_value_is_greater_than_mean_plus_3_stds(self):
        row = pd.Series({'applicant_id': 444,
                         'subquota_description': 'Congressperson meal',
                         'cnpj_cpf': '67661714000111',
                         'supplier': 'B Restaurant',
                         'total_net_value': 178})
        X = pd.DataFrame().append(row, ignore_index=True)
        prediction = self.subject.predict(X)
        self.assertEqual(-1, prediction[0])

    def test_predict_inlier_for_common_cnpjs_when_value_is_less_than_mean_plus_3_stds(self):
        row = pd.Series({'applicant_id': 444,
                         'subquota_description': 'Congressperson meal',
                         'cnpj_cpf': '67661714000111',
                         'supplier': 'B Restaurant',
                         'total_net_value': 177})
        X = pd.DataFrame().append(row, ignore_index=True)
        prediction = self.subject.predict(X)
        self.assertEqual(1, prediction[0])

    def test_predict_outlier_for_non_common_cnpjs_when_value_is_greater_than_mean_plus_4_stds(self):
        row = pd.Series({'applicant_id': 444,
                         'subquota_description': 'Congressperson meal',
                         'cnpj_cpf': '22412242000125',
                         'supplier': 'D Restaurant',
                         'total_net_value': 178})
        X = pd.DataFrame().append(row, ignore_index=True)
        prediction = self.subject.predict(X)
        self.assertEqual(-1, prediction[0])

    def test_predict_inlier_for_non_common_cnpjs_when_value_is_less_than_mean_plus_4_stds(self):
        row = pd.Series({'applicant_id': 444,
                         'subquota_description': 'Congressperson meal',
                         'cnpj_cpf': '22412242000125',
                         'supplier': 'D Restaurant',
                         'total_net_value': 177})
        X = pd.DataFrame().append(row, ignore_index=True)
        prediction = self.subject.predict(X)
        self.assertEqual(1, prediction[0])

    def test_predict_inlier_for_non_meal_reimbursement_with_large_value(self):
        prediction = self.subject.predict(self.dataset)
        self.assertEqual(1, prediction[72])

    def test_predict_inlier_for_meal_reimbursement_with_small_value(self):
        prediction = self.subject.predict(self.dataset)
        self.assertEqual(1, prediction[73])

    def test_predict_inlier_for_reimbursement_with_small_value(self):
        prediction = self.subject.predict(self.dataset)
        self.assertEqual(1, prediction[7])

    def test_predict_inlier_for_meals_with_large_values_in_hotels(self):
        prediction = self.subject.predict(self.dataset)
        assert_array_equal(np.ones(3), prediction[4:7])

    def test_predict_inlier_for_meals_with_small_values_in_hotels(self):
        prediction = self.subject.predict(self.dataset)
        assert_array_equal(np.ones(3), prediction[1:4])

    def test_predict_inlier_for_meals_with_cpfs(self):
        prediction = self.subject.predict(self.dataset)
        self.assertEqual(1, prediction[0])


if __name__ == '__main__':
    unittest.main()