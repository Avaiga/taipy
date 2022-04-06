# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from importlib import util

import numpy as np
import pandas as pd

from taipy.gui.data.utils import _df_data_filter


def test_data_filter_1(csvdata):
    df, x, y = _df_data_filter(csvdata[:1500], None, "Daily hospital occupancy", 100)
    if not util.find_spec("rdp"):
        assert df.shape[0] == 1500
        assert x is None
    else:
        assert df.shape[0] == 121
        assert x == "tAiPy_index_0"
    assert y == "Daily hospital occupancy"


def test_data_filter_2(csvdata):
    df, x, y = _df_data_filter(csvdata[:1500], None, "Daily hospital occupancy", 1500)
    assert df.shape[0] == 1500
    assert x is None
    assert y == "Daily hospital occupancy"


def test_data_filter_3(csvdata):
    csvdata["DayInt"] = pd.to_datetime(csvdata["Day"]).view(np.int64)
    df, x, y = _df_data_filter(csvdata[:1500], "DayInt", "Daily hospital occupancy", 100)
    if not util.find_spec("rdp"):
        assert df.shape[0] == 1500
    else:
        assert df.shape[0] == 121
    assert x == "DayInt"
    assert y == "Daily hospital occupancy"
