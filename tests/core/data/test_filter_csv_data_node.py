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

import os
import pathlib

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.operator import JoinOperator, Operator


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")
    if os.path.isfile(path):
        os.remove(path)


class MyCustomObject:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


def test_filter_pandas_exposed_type(csv_file):
    dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "pandas"})
    dn.write(
        [
            {"foo": 1, "bar": 1},
            {"foo": 1, "bar": 2},
            {"foo": 1},
            {"foo": 2, "bar": 2},
            {"bar": 2},
        ]
    )

    # Test datanode indexing and slicing
    assert dn["foo"].equals(pd.Series([1, 1, 1, 2, None]))
    assert dn["bar"].equals(pd.Series([1, 2, None, 2, 2]))
    assert dn[:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

    # Test filter data
    filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
    filtered_by_indexing = dn[dn["foo"] == 1]
    expected_data = pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}, {"foo": 1.0}])
    assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
    assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

    filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
    filtered_by_indexing = dn[dn["foo"] != 1]
    expected_data = pd.DataFrame([{"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
    assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
    assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

    filtered_by_filter_method = dn.filter(("bar", 2, Operator.EQUAL))
    filtered_by_indexing = dn[dn["bar"] == 2]
    expected_data = pd.DataFrame([{"foo": 1.0, "bar": 2.0}, {"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
    assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
    assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

    filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
    filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
    expected_data = pd.DataFrame(
        [
            {"foo": 1.0, "bar": 1.0},
            {"foo": 1.0, "bar": 2.0},
            {"foo": 2.0, "bar": 2.0},
            {"bar": 2.0},
        ]
    )
    assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
    assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)


def test_filter_numpy_exposed_type(csv_file):
    dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "numpy"})
    dn.write(
        np.array(
            [
                [1, 1],
                [1, 2],
                [1, 3],
                [2, 1],
                [2, 2],
                [2, 3],
            ]
        )
    )

    # Test datanode indexing and slicing
    assert np.array_equal(dn[0], np.array([1, 1]))
    assert np.array_equal(dn[1], np.array([1, 2]))
    assert np.array_equal(dn[:3], np.array([[1, 1], [1, 2], [1, 3]]))
    assert np.array_equal(dn[:, 0], np.array([1, 1, 1, 2, 2, 2]))
    assert np.array_equal(dn[1:4, :1], np.array([[1], [1], [2]]))

    # Test filter data
    assert np.array_equal(dn.filter((0, 1, Operator.EQUAL)), np.array([[1, 1], [1, 2], [1, 3]]))
    assert np.array_equal(dn[dn[:, 0] == 1], np.array([[1, 1], [1, 2], [1, 3]]))

    assert np.array_equal(dn.filter((0, 1, Operator.NOT_EQUAL)), np.array([[2, 1], [2, 2], [2, 3]]))
    assert np.array_equal(dn[dn[:, 0] != 1], np.array([[2, 1], [2, 2], [2, 3]]))

    assert np.array_equal(dn.filter((1, 2, Operator.EQUAL)), np.array([[1, 2], [2, 2]]))
    assert np.array_equal(dn[dn[:, 1] == 2], np.array([[1, 2], [2, 2]]))

    assert np.array_equal(
        dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR),
        np.array([[1, 1], [1, 2], [2, 1], [2, 2]]),
    )
    assert np.array_equal(dn[(dn[:, 1] == 1) | (dn[:, 1] == 2)], np.array([[1, 1], [1, 2], [2, 1], [2, 2]]))
