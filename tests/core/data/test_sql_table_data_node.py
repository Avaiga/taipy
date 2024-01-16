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

from importlib import util
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.data.sql_table import SQLTableDataNode
from taipy.core.exceptions.exceptions import InvalidExposedType, MissingRequiredProperty


class MyCustomObject:
    def __init__(self, foo=None, bar=None, *args, **kwargs):
        self.foo = foo
        self.bar = bar
        self.args = args
        self.kwargs = kwargs


class TestSQLTableDataNode:
    __pandas_properties = [
        {
            "db_name": "taipy",
            "db_engine": "sqlite",
            "table_name": "example",
            "db_extra_args": {
                "TrustServerCertificate": "yes",
                "other": "value",
            },
        },
    ]

    if util.find_spec("pyodbc"):
        __pandas_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mssql",
                "table_name": "example",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    if util.find_spec("pymysql"):
        __pandas_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mysql",
                "table_name": "example",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    if util.find_spec("psycopg2"):
        __pandas_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "postgresql",
                "table_name": "example",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_create(self, pandas_properties):
        dn = SQLTableDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties=pandas_properties,
        )
        assert isinstance(dn, SQLTableDataNode)
        assert dn.storage_type() == "sql_table"
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.exposed_type == "pandas"
        assert dn.table_name == "example"
        assert dn._get_base_read_query() == "SELECT * FROM example"

    @pytest.mark.parametrize("properties", __pandas_properties)
    def test_get_user_properties(self, properties):
        custom_properties = properties.copy()
        custom_properties["foo"] = "bar"
        dn = SQLTableDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties=custom_properties,
        )
        assert dn._get_user_properties() == {"foo": "bar"}

    @pytest.mark.parametrize(
        "properties",
        [
            {},
            {"db_username": "foo"},
            {"db_username": "foo", "db_password": "foo"},
            {"db_username": "foo", "db_password": "foo", "db_name": "foo"},
        ],
    )
    def test_create_with_missing_parameters(self, properties):
        with pytest.raises(MissingRequiredProperty):
            SQLTableDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            SQLTableDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)

    @patch("taipy.core.data.sql_table.SQLTableDataNode._read_as_pandas_dataframe", return_value="pandas")
    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_modin_deprecated_in_favor_of_pandas(self, mock_read_as_pandas_dataframe, pandas_properties):
        pandas_properties["exposed_type"] = "modin"
        sql_data_node_as_modin = SQLTableDataNode("foo", Scope.SCENARIO, properties=pandas_properties)
        assert sql_data_node_as_modin.properties["exposed_type"] == "pandas"
        assert sql_data_node_as_modin.read() == "pandas"

    @patch("taipy.core.data.sql_table.SQLTableDataNode._read_as", return_value="custom")
    @patch("taipy.core.data.sql_table.SQLTableDataNode._read_as_pandas_dataframe", return_value="pandas")
    @patch("taipy.core.data.sql_table.SQLTableDataNode._read_as_numpy", return_value="numpy")
    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_read(
        self,
        mock_read_as,
        mock_read_as_pandas_dataframe,
        mock_read_as_numpy,
        pandas_properties,
    ):
        custom_properties = pandas_properties.copy()
        # Create SQLTableDataNode without exposed_type (Default is pandas.DataFrame)
        sql_data_node_as_pandas = SQLTableDataNode(
            "foo",
            Scope.SCENARIO,
            properties=pandas_properties,
        )

        assert sql_data_node_as_pandas.read() == "pandas"

        custom_properties.pop("db_extra_args")
        custom_properties["exposed_type"] = MyCustomObject
        # Create the same SQLTableDataNode but with custom exposed_type
        sql_data_node_as_custom_object = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)
        assert sql_data_node_as_custom_object.read() == "custom"

        # Create the same SQLDataSource but with numpy exposed_type
        custom_properties["exposed_type"] = "numpy"
        sql_data_source_as_numpy_object = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        assert sql_data_source_as_numpy_object.read() == "numpy"


    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_read_as(self, pandas_properties):
        custom_properties = pandas_properties.copy()

        custom_properties.pop("db_extra_args")
        custom_properties["exposed_type"] = MyCustomObject
        sql_data_node = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.return_value = [
                {"foo": "baz", "bar": "qux"},
                {"foo": "quux", "bar": "quuz"},
                {"foo": "corge"},
                {"bar": "grault"},
                {"KWARGS_KEY": "KWARGS_VALUE"},
                {},
            ]
            data = sql_data_node._read_as()

        assert isinstance(data, list)
        assert isinstance(data[0], MyCustomObject)
        assert isinstance(data[1], MyCustomObject)
        assert isinstance(data[2], MyCustomObject)
        assert isinstance(data[3], MyCustomObject)
        assert isinstance(data[4], MyCustomObject)
        assert isinstance(data[5], MyCustomObject)

        assert data[0].foo == "baz"
        assert data[0].bar == "qux"
        assert data[1].foo == "quux"
        assert data[1].bar == "quuz"
        assert data[2].foo == "corge"
        assert data[2].bar is None
        assert data[3].foo is None
        assert data[3].bar == "grault"
        assert data[4].foo is None
        assert data[4].bar is None
        assert data[4].kwargs["KWARGS_KEY"] == "KWARGS_VALUE"
        assert data[5].foo is None
        assert data[5].bar is None
        assert len(data[5].args) == 0
        assert len(data[5].kwargs) == 0

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.return_value = []
            data_2 = sql_data_node._read_as()
        assert isinstance(data_2, list)
        assert len(data_2) == 0

    @pytest.mark.parametrize(
        "data,written_data,called_func",
        [
            ([{"a": 1, "b": 2}, {"a": 3, "b": 4}], [{"a": 1, "b": 2}, {"a": 3, "b": 4}], "__insert_dicts"),
            ({"a": 1, "b": 2}, [{"a": 1, "b": 2}], "__insert_dicts"),
            ([(1, 2), (3, 4)], [(1, 2), (3, 4)], "__insert_tuples"),
            ([[1, 2], [3, 4]], [[1, 2], [3, 4]], "__insert_tuples"),
            ((1, 2), [(1, 2)], "__insert_tuples"),
            ([1, 2, 3, 4], [(1,), (2,), (3,), (4,)], "__insert_tuples"),
            ("foo", [("foo",)], "__insert_tuples"),
            (None, [(None,)], "__insert_tuples"),
            (np.array([1, 2, 3, 4]), [(1,), (2,), (3,), (4,)], "__insert_tuples"),
            (np.array([np.array([1, 2]), np.array([3, 4])]), [[1, 2], [3, 4]], "__insert_tuples"),
        ],
    )
    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_write_1(self, data, written_data, called_func, pandas_properties):
        custom_properties = pandas_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ) as create_table_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            with patch(f"taipy.core.data.sql_table.SQLTableDataNode._SQLTableDataNode{called_func}") as mck:
                dn.write(data)
                mck.assert_called_once_with(written_data, create_table_mock.return_value, cursor_mock, True)

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_raise_error_invalid_exposed_type(self, pandas_properties):
        custom_properties = pandas_properties.copy()
        custom_properties.pop("db_extra_args")
        custom_properties["exposed_type"] = "foo"
        with pytest.raises(InvalidExposedType):
            SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_write_dataframe(self, pandas_properties):
        # test write pandas dataframe
        custom_properties = pandas_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [5, 6, 7, 8]})
        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ):
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            with patch("taipy.core.data.sql_table.SQLTableDataNode._SQLTableDataNode__insert_dataframe") as mck:
                dn.write(df)
                assert mck.call_args[0][0].equals(df)

    @pytest.mark.parametrize(
        "data",
        [
            [],
            np.array([]),
        ],
    )
    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    def test_write_empty_list(self, data, pandas_properties):
        custom_properties = pandas_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ) as create_table_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            with patch("taipy.core.data.sql_table.SQLTableDataNode._SQLTableDataNode__delete_all_rows") as mck:
                dn.write(data)
                mck.assert_called_once_with(create_table_mock.return_value, cursor_mock, True)

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    @patch("pandas.read_sql_query")
    def test_engine_cache(self, _, pandas_properties):
        dn = SQLTableDataNode(
            "foo",
            Scope.SCENARIO,
            properties=pandas_properties,
        )

        assert dn._engine is None

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ):
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            dn.read()
            assert dn._engine is not None

            dn.db_username = "foo"
            assert dn._engine is None

            dn.write(1)
            assert dn._engine is not None

            dn.some_random_attribute_that_does_not_related_to_engine = "foo"
            assert dn._engine is not None

    @pytest.mark.parametrize(
        "tmp_sqlite_path",
        [
            "tmp_sqlite_db_file_path",
            "tmp_sqlite_sqlite3_file_path",
        ],
    )
    def test_sqlite_read_file_with_different_extension(self, tmp_sqlite_path, request):
        tmp_sqlite_path = request.getfixturevalue(tmp_sqlite_path)
        folder_path, db_name, file_extension = tmp_sqlite_path
        properties = {
            "db_engine": "sqlite",
            "table_name": "example",
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
        }

        dn = SQLTableDataNode("sqlite_dn", Scope.SCENARIO, properties=properties)
        data = dn.read()

        assert data.equals(pd.DataFrame([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}]))

    def test_sqlite_append_pandas(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "table_name": "example",
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
        }

        dn = SQLTableDataNode("sqlite_dn", Scope.SCENARIO, properties=properties)
        original_data = pd.DataFrame([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}])
        data = dn.read()
        assert_frame_equal(data, original_data)

        append_data_1 = pd.DataFrame([{"foo": 5, "bar": 6}, {"foo": 7, "bar": 8}])
        dn.append(append_data_1)
        assert_frame_equal(dn.read(), pd.concat([original_data, append_data_1]).reset_index(drop=True))

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
