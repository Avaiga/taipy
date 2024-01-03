# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import numpy as np
import pandas as pd

from taipy.gui.data.decimator.lttb import LTTB
from taipy.gui.data.decimator.minmax import MinMaxDecimator
from taipy.gui.data.decimator.rdp import RDP
from taipy.gui.data.decimator.scatter_decimator import ScatterDecimator
from taipy.gui.data.utils import _df_data_filter


def test_data_filter_1(csvdata):
    df, _ = _df_data_filter(csvdata[:1500], None, "Daily hospital occupancy", "", MinMaxDecimator(100), {}, False)
    assert df.shape[0] == 100


def test_data_filter_2(csvdata):
    df, _ = _df_data_filter(csvdata[:1500], None, "Daily hospital occupancy", "", LTTB(100), {}, False)
    assert df.shape[0] == 100


def test_data_filter_3(csvdata):
    df, _ = _df_data_filter(csvdata[:1500], None, "Daily hospital occupancy", "", RDP(n_out=100), {}, False)
    assert df.shape[0] == 100


def test_data_filter_4(csvdata):
    df, _ = _df_data_filter(csvdata[:1500], None, "Daily hospital occupancy", "", RDP(epsilon=100), {}, False)
    assert df.shape[0] == 18


def test_data_filter_5(csvdata):
    df, _ = _df_data_filter(
        csvdata[:1500], None, "Daily hospital occupancy", "", ScatterDecimator(), {"width": 200, "height": 100}, False
    )
    assert df.shape[0] == 1150
