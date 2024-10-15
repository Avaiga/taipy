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

from taipy.common.config.common.scope import Scope
from taipy.core.data.excel import ExcelDataNode
from taipy.core.data.operator import JoinOperator, Operator


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.xlsx")
    if os.path.exists(path):
        os.remove(path)


def test_filter_pandas_exposed_type_with_sheetname(excel_file):
    dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "pandas"}
    )
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


def test_filter_pandas_exposed_type_without_sheetname(excel_file):
    dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "exposed_type": "pandas"})
    dn.write(
        [
            {"foo": 1, "bar": 1},
            {"foo": 1, "bar": 2},
            {"foo": 1},
            {"foo": 2, "bar": 2},
            {"bar": 2},
        ]
    )

    assert len(dn.filter(("foo", 1, Operator.EQUAL))["Sheet1"]) == 3
    assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["Sheet1"]) == 2
    assert len(dn.filter(("bar", 2, Operator.EQUAL))["Sheet1"]) == 3
    assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["Sheet1"]) == 4

    assert dn["Sheet1"]["foo"].equals(pd.Series([1, 1, 1, 2, None]))
    assert dn["Sheet1"]["bar"].equals(pd.Series([1, 2, None, 2, 2]))
    assert dn["Sheet1"][:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))


def test_filter_pandas_exposed_type_multisheet(excel_file):
    dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": excel_file, "sheet_name": ["sheet_1", "sheet_2"], "exposed_type": "pandas"},
    )
    dn.write(
        {
            "sheet_1": pd.DataFrame(
                [
                    {"foo": 1, "bar": 1},
                    {"foo": 1, "bar": 2},
                    {"foo": 1},
                    {"foo": 2, "bar": 2},
                    {"bar": 2},
                ]
            ),
            "sheet_2": pd.DataFrame(
                [
                    {"foo": 1, "bar": 3},
                    {"foo": 1, "bar": 4},
                    {"foo": 1},
                    {"foo": 2, "bar": 4},
                    {"bar": 4},
                ]
            ),
        }
    )

    assert len(dn.filter(("foo", 1, Operator.EQUAL))) == 2
    assert len(dn.filter(("foo", 1, Operator.EQUAL))["sheet_1"]) == 3
    assert len(dn.filter(("foo", 1, Operator.EQUAL))["sheet_2"]) == 3

    assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))) == 2
    assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["sheet_1"]) == 2
    assert len(dn.filter(("foo", 1, Operator.NOT_EQUAL))["sheet_2"]) == 2

    assert len(dn.filter(("bar", 2, Operator.EQUAL))) == 2
    assert len(dn.filter(("bar", 2, Operator.EQUAL))["sheet_1"]) == 3
    assert len(dn.filter(("bar", 2, Operator.EQUAL))["sheet_2"]) == 0

    assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)) == 2
    assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["sheet_1"]) == 4
    assert len(dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)["sheet_2"]) == 0

    assert dn["sheet_1"]["foo"].equals(pd.Series([1, 1, 1, 2, None]))
    assert dn["sheet_2"]["foo"].equals(pd.Series([1, 1, 1, 2, None]))
    assert dn["sheet_1"]["bar"].equals(pd.Series([1, 2, None, 2, 2]))
    assert dn["sheet_2"]["bar"].equals(pd.Series([3, 4, None, 4, 4]))
    assert dn["sheet_1"][:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))
    assert dn["sheet_2"][:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 3.0}, {"foo": 1.0, "bar": 4.0}]))


def test_filter_numpy_exposed_type_with_sheetname(excel_file):
    dn = ExcelDataNode(
        "foo", Scope.SCENARIO, properties={"path": excel_file, "sheet_name": "Sheet1", "exposed_type": "numpy"}
    )
    dn.write(
        [
            [1, 1],
            [1, 2],
            [1, 3],
            [2, 1],
            [2, 2],
            [2, 3],
        ]
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


def test_filter_numpy_exposed_type_without_sheetname(excel_file):
    dn = ExcelDataNode("foo", Scope.SCENARIO, properties={"path": excel_file, "exposed_type": "numpy"})
    dn.write(
        [
            [1, 1],
            [1, 2],
            [1, 3],
            [2, 1],
            [2, 2],
            [2, 3],
        ]
    )

    assert len(dn.filter((0, 1, Operator.EQUAL))["Sheet1"]) == 3
    assert len(dn.filter((0, 1, Operator.NOT_EQUAL))["Sheet1"]) == 3
    assert len(dn.filter((1, 2, Operator.EQUAL))["Sheet1"]) == 2
    assert len(dn.filter([(0, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)["Sheet1"]) == 4

    assert np.array_equal(dn["Sheet1"][0], np.array([1, 1]))
    assert np.array_equal(dn["Sheet1"][1], np.array([1, 2]))
    assert np.array_equal(dn["Sheet1"][:3], np.array([[1, 1], [1, 2], [1, 3]]))
    assert np.array_equal(dn["Sheet1"][:, 0], np.array([1, 1, 1, 2, 2, 2]))
    assert np.array_equal(dn["Sheet1"][1:4, :1], np.array([[1], [1], [2]]))


def test_filter_numpy_exposed_type_multisheet(excel_file):
    dn = ExcelDataNode(
        "foo",
        Scope.SCENARIO,
        properties={"path": excel_file, "sheet_name": ["sheet_1", "sheet_2"], "exposed_type": "numpy"},
    )
    dn.write(
        {
            "sheet_1": pd.DataFrame(
                [
                    [1, 1],
                    [1, 2],
                    [1, 3],
                    [2, 1],
                    [2, 2],
                    [2, 3],
                ]
            ),
            "sheet_2": pd.DataFrame(
                [
                    [1, 4],
                    [1, 5],
                    [1, 6],
                    [2, 4],
                    [2, 5],
                    [2, 6],
                ]
            ),
        }
    )

    assert len(dn.filter((0, 1, Operator.EQUAL))) == 2
    assert len(dn.filter((0, 1, Operator.EQUAL))["sheet_1"]) == 3
    assert len(dn.filter((0, 1, Operator.EQUAL))["sheet_2"]) == 3

    assert len(dn.filter((0, 1, Operator.NOT_EQUAL))) == 2
    assert len(dn.filter((0, 1, Operator.NOT_EQUAL))["sheet_1"]) == 3
    assert len(dn.filter((0, 1, Operator.NOT_EQUAL))["sheet_2"]) == 3

    assert len(dn.filter((1, 2, Operator.EQUAL))) == 2
    assert len(dn.filter((1, 2, Operator.EQUAL))["sheet_1"]) == 2
    assert len(dn.filter((1, 2, Operator.EQUAL))["sheet_2"]) == 0

    assert len(dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)) == 2
    assert len(dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)["sheet_1"]) == 4
    assert len(dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR)["sheet_2"]) == 0

    assert np.array_equal(dn["sheet_1"][0], np.array([1, 1]))
    assert np.array_equal(dn["sheet_2"][0], np.array([1, 4]))
    assert np.array_equal(dn["sheet_1"][1], np.array([1, 2]))
    assert np.array_equal(dn["sheet_2"][1], np.array([1, 5]))
    assert np.array_equal(dn["sheet_1"][:3], np.array([[1, 1], [1, 2], [1, 3]]))
    assert np.array_equal(dn["sheet_2"][:3], np.array([[1, 4], [1, 5], [1, 6]]))
    assert np.array_equal(dn["sheet_1"][:, 0], np.array([1, 1, 1, 2, 2, 2]))
    assert np.array_equal(dn["sheet_2"][:, 1], np.array([4, 5, 6, 4, 5, 6]))
    assert np.array_equal(dn["sheet_1"][1:4, :1], np.array([[1], [1], [2]]))
    assert np.array_equal(dn["sheet_2"][1:4, 1:2], np.array([[5], [6], [4]]))
