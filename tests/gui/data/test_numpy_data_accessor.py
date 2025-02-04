# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
from importlib import util

import numpy
import pandas

from taipy.gui import Gui
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.data.numpy_data_accessor import _NumpyDataAccessor

a_numpy_array = numpy.array([1, 2, 3])


def test_simple_data(gui: Gui, helpers):
    accessor = _NumpyDataAccessor(gui)
    ret_data = accessor.get_data("x", a_numpy_array, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 3


def test_simple_data_with_arrow(gui: Gui, helpers):
    if util.find_spec("pyarrow"):
        accessor = _NumpyDataAccessor(gui)
        ret_data = accessor.get_data("x", a_numpy_array, {"start": 0, "end": -1}, _DataFormat.APACHE_ARROW)
        assert ret_data
        value = ret_data["value"]
        assert value
        assert value["rowcount"] == 3
        data = value["data"]
        assert isinstance(data, bytes)


def test_slice(gui: Gui, helpers):
    accessor = _NumpyDataAccessor(gui)
    value = accessor.get_data("x", a_numpy_array, {"start": 0, "end": 1}, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 2
    value = accessor.get_data("x", a_numpy_array, {"start": "0", "end": "1"}, _DataFormat.JSON)["value"]
    data = value["data"]
    assert len(data) == 2


def test_csv(gui, small_dataframe):
    accessor = _NumpyDataAccessor(gui)
    pd = small_dataframe
    path = accessor.to_csv("", pd)
    assert path is not None
    assert os.path.getsize(path) > 0

def test__from_pandas(gui):
    accessor = _NumpyDataAccessor(gui)
    ad = accessor._from_pandas(pandas.DataFrame(a_numpy_array), numpy.ndarray)
    assert isinstance(ad, numpy.ndarray)
    assert len(ad) == 3

