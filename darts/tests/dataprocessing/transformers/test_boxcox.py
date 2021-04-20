import unittest
import pandas as pd
from math import log

from darts.dataprocessing.transformers import BoxCox, Mapper
from darts.utils.timeseries_generation import sine_timeseries, linear_timeseries


class BoxCoxTestCase(unittest.TestCase):

    sine_series = sine_timeseries(length=50, value_y_offset=5, value_frequency=0.05)
    lin_series = linear_timeseries(start_value=1, end_value=10, length=50)
    multi_series = sine_series.stack(lin_series)

    def test_boxbox_lambda(self):
        boxcox = BoxCox(lmbda=0.3)

        boxcox.fit(self.multi_series)
        self.assertEqual(boxcox._lmbda, [0.3, 0.3])

        boxcox = BoxCox(lmbda=[0.3, 0.4])
        boxcox.fit(self.multi_series)
        self.assertEqual(boxcox._lmbda, [0.3, 0.4])

        with self.assertRaises(ValueError):
            boxcox = BoxCox(lmbda=[0.2, 0.4, 0.5])
            boxcox.fit(self.multi_series)

        boxcox = BoxCox()
        boxcox.fit(self.multi_series, optim_method='mle')
        lmbda1 = boxcox._lmbda
        boxcox.fit(self.multi_series, optim_method='pearsonr')
        lmbda2 = boxcox._lmbda

        self.assertNotEqual(lmbda1.array, lmbda2.array)

    def test_boxcox_transform(self):
        log_mapper = Mapper(lambda x: log(x))
        boxcox = BoxCox(lmbda=0)

        transformed1 = log_mapper.transform(self.sine_series)
        transformed2 = boxcox.fit(self.sine_series).transform(self.sine_series)

        self.assertEqual(transformed1, transformed2)

    def test_boxcox_inverse(self):
        boxcox = BoxCox()
        transformed = boxcox.fit_transform(self.multi_series)
        back = boxcox.inverse_transform(transformed)
        pd.testing.assert_frame_equal(self.multi_series._df, back._df, check_exact=False)

    def test_boxcox_multi_ts(self):
        # with full lambdas values
        box_cox = BoxCox(lmbda=[[0.2, 0.4], [0.3, 0.6]])
        transformed = box_cox.fit_transform([self.multi_series, self.multi_series])
        back = box_cox.inverse_transform(transformed)
        pd.testing.assert_frame_equal(self.multi_series._df, back[0]._df, check_exact=False)
        pd.testing.assert_frame_equal(self.multi_series._df, back[1]._df, check_exact=False)

        # single lambda
        box_cox = BoxCox(lmbda=0.4)
        transformed = box_cox.fit_transform([self.multi_series, self.multi_series])
        back = box_cox.inverse_transform(transformed)
        pd.testing.assert_frame_equal(self.multi_series._df, back[0]._df, check_exact=False)
        pd.testing.assert_frame_equal(self.multi_series._df, back[1]._df, check_exact=False)

        # lambda = None
        box_cox = BoxCox()
        transformed = box_cox.fit_transform([self.multi_series, self.multi_series])
        back = box_cox.inverse_transform(transformed)
        pd.testing.assert_frame_equal(self.multi_series._df, back[0]._df, check_exact=False)
        pd.testing.assert_frame_equal(self.multi_series._df, back[1]._df, check_exact=False)
