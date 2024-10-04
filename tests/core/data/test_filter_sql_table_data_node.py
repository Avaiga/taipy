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

from unittest.mock import patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from taipy.common.config.common.scope import Scope
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.data.sql_table import SQLTableDataNode


class MyCustomObject:
    def __init__(self, foo=None, bar=None, *args, **kwargs):
        self.foo = foo
        self.bar = bar
        self.args = args
        self.kwargs = kwargs


class TestFilterSQLTableDataNode:
    def test_filter_pandas_exposed_type(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "table_name": "example",
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "pandas",
        }
        dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=properties)
        dn.write(
            pd.DataFrame(
                [
                    {"foo": 1, "bar": 1},
                    {"foo": 1, "bar": 2},
                    {"foo": 1, "bar": 3},
                    {"foo": 2, "bar": 1},
                    {"foo": 2, "bar": 2},
                    {"foo": 2, "bar": 3},
                ]
            )
        )

        # Test datanode indexing and slicing
        assert dn["foo"].equals(pd.Series([1, 1, 1, 2, 2, 2]))
        assert dn["bar"].equals(pd.Series([1, 2, 3, 1, 2, 3]))
        assert dn[:2].equals(pd.DataFrame([{"foo": 1, "bar": 1}, {"foo": 1, "bar": 2}]))

        # Test filter data
        filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
        filtered_by_indexing = dn[dn["foo"] == 1]
        expected_data = pd.DataFrame([{"foo": 1, "bar": 1}, {"foo": 1, "bar": 2}, {"foo": 1, "bar": 3}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
        filtered_by_indexing = dn[dn["foo"] != 1]
        expected_data = pd.DataFrame([{"foo": 2, "bar": 1}, {"foo": 2, "bar": 2}, {"foo": 2, "bar": 3}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
        filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
        expected_data = pd.DataFrame(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 2, "bar": 1},
                {"foo": 2, "bar": 2},
            ]
        )
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

    def test_filter_numpy_exposed_type(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "table_name": "example",
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "numpy",
        }
        dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=properties)
        dn.write(
            pd.DataFrame(
                [
                    {"foo": 1, "bar": 1},
                    {"foo": 1, "bar": 2},
                    {"foo": 1, "bar": 3},
                    {"foo": 2, "bar": 1},
                    {"foo": 2, "bar": 2},
                    {"foo": 2, "bar": 3},
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
        assert np.array_equal(dn.filter(("foo", 1, Operator.EQUAL)), np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn[dn[:, 0] == 1], np.array([[1, 1], [1, 2], [1, 3]]))

        assert np.array_equal(dn.filter(("foo", 1, Operator.NOT_EQUAL)), np.array([[2, 1], [2, 2], [2, 3]]))
        assert np.array_equal(dn[dn[:, 0] != 1], np.array([[2, 1], [2, 2], [2, 3]]))

        assert np.array_equal(dn.filter(("bar", 2, Operator.EQUAL)), np.array([[1, 2], [2, 2]]))
        assert np.array_equal(dn[dn[:, 1] == 2], np.array([[1, 2], [2, 2]]))

        assert np.array_equal(
            dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR),
            np.array([[1, 1], [1, 2], [2, 1], [2, 2]]),
        )
        assert np.array_equal(dn[(dn[:, 1] == 1) | (dn[:, 1] == 2)], np.array([[1, 1], [1, 2], [2, 1], [2, 2]]))

    def test_filter_does_not_read_all_entities(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "table_name": "example",
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "numpy",
        }
        dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=properties)

        # SQLTableDataNode.filter() should not call the MongoCollectionDataNode._read() method
        with patch.object(SQLTableDataNode, "_read") as read_mock:
            dn.filter(("foo", 1, Operator.EQUAL))
            dn.filter(("bar", 2, Operator.NOT_EQUAL))
            dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)

            assert read_mock["_read"].call_count == 0
