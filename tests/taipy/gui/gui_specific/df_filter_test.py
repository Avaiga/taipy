import numpy as np
import pandas as pd

from taipy.gui.data.utils import df_data_filter


def test_data_filter_1(csvdata):
    df, x, y = df_data_filter(csvdata, None, "Daily hospital occupancy", 1000)
    assert df.shape[0] == 1264
    assert x == "tAiPy_index_0"
    assert y == "Daily hospital occupancy"


def test_data_filter_2(csvdata):
    df, x, y = df_data_filter(csvdata, None, "Daily hospital occupancy", 15000)
    assert df.shape[0] == 14477
    assert x is None
    assert y == "Daily hospital occupancy"


def test_data_filter_3(csvdata):
    csvdata["DayInt"] = pd.to_datetime(csvdata["Day"]).astype(np.int64)
    df, x, y = df_data_filter(csvdata, "DayInt", "Daily hospital occupancy", 1000)
    assert df.shape[0] == 1451
    assert x == "DayInt"
    assert y == "Daily hospital occupancy"
