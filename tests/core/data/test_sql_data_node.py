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

from taipy.config import Config
from taipy.config.common.scope import Scope
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.data.sql import SQLDataNode
from taipy.core.exceptions.exceptions import MissingAppendQueryBuilder, MissingRequiredProperty


class MyCustomObject:
    def __init__(self, foo=None, bar=None, *args, **kwargs):
        self.foo = foo
        self.bar = bar
        self.args = args
        self.kwargs = kwargs


def my_write_query_builder_with_pandas(data: pd.DataFrame):
    insert_data = data.to_dict("records")
    return ["DELETE FROM example", ("INSERT INTO example VALUES (:foo, :bar)", insert_data)]


def my_append_query_builder_with_pandas(data: pd.DataFrame):
    insert_data = data.to_dict("records")
    return [("INSERT INTO example VALUES (:foo, :bar)", insert_data)]


def single_write_query_builder(data):
    return "DELETE FROM example"


class TestSQLDataNode:
    __sql_properties = [
        {
            "db_name": "taipy.sqlite3",
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_pandas,
            "db_extra_args": {
                "TrustServerCertificate": "yes",
                "other": "value",
            },
        },
    ]

    if util.find_spec("pyodbc"):
        __sql_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mssql",
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_pandas,
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    if util.find_spec("pymysql"):
        __sql_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mysql",
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_pandas,
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    if util.find_spec("psycopg2"):
        __sql_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "postgresql",
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_pandas,
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_create(self, properties):
        sql_dn_config = Config.configure_sql_data_node(id="foo_bar", **properties)
        dn = _DataManagerFactory._build_manager()._create_and_set(sql_dn_config, None, None)
        assert isinstance(dn, SQLDataNode)
        assert dn.storage_type() == "sql"
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.exposed_type == "pandas"
        assert dn.read_query == "SELECT * FROM example"
        assert dn.write_query_builder == my_write_query_builder_with_pandas

        sql_dn_config_1 = Config.configure_sql_data_node(
            id="foo",
            **properties,
            append_query_builder=my_append_query_builder_with_pandas,
            exposed_type=MyCustomObject,
        )
        dn_1 = _DataManagerFactory._build_manager()._create_and_set(sql_dn_config_1, None, None)
        assert isinstance(dn, SQLDataNode)
        assert dn_1.exposed_type == MyCustomObject
        assert dn_1.append_query_builder == my_append_query_builder_with_pandas

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_get_user_properties(self, properties):
        custom_properties = properties.copy()
        custom_properties["foo"] = "bar"
        dn = SQLDataNode(
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
            {"engine": "sqlite"},
            {"engine": "mssql", "db_name": "foo"},
            {"engine": "mysql", "db_username": "foo"},
            {"engine": "postgresql", "db_username": "foo", "db_password": "foo"},
        ],
    )
    def test_create_with_missing_parameters(self, properties):
        with pytest.raises(MissingRequiredProperty):
            SQLDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            SQLDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_write_query_builder(self, properties):
        custom_properties = properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLDataNode("foo_bar", Scope.SCENARIO, properties=custom_properties)
        with patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert len(engine_mock.mock_calls[4].args) == 1
            assert engine_mock.mock_calls[4].args[0].text == "DELETE FROM example"
            assert len(engine_mock.mock_calls[5].args) == 2
            assert engine_mock.mock_calls[5].args[0].text == "INSERT INTO example VALUES (:foo, :bar)"
            assert engine_mock.mock_calls[5].args[1] == [
                {"foo": 1, "bar": 4},
                {"foo": 2, "bar": 5},
                {"foo": 3, "bar": 6},
            ]

        custom_properties["write_query_builder"] = single_write_query_builder
        dn = SQLDataNode("foo_bar", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert len(engine_mock.mock_calls[4].args) == 1
            assert engine_mock.mock_calls[4].args[0].text == "DELETE FROM example"

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
            "read_query": "SELECT * from example",
            "write_query_builder": single_write_query_builder,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
        }

        dn = SQLDataNode("sqlite_dn", Scope.SCENARIO, properties=properties)
        data = dn.read()
        assert data.equals(pd.DataFrame([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}]))

    def test_sqlite_append_pandas(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_pandas,
            "append_query_builder": my_append_query_builder_with_pandas,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
        }

        dn = SQLDataNode("sqlite_dn", Scope.SCENARIO, properties=properties)
        original_data = pd.DataFrame([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}])
        data = dn.read()
        assert_frame_equal(data, original_data)

        append_data_1 = pd.DataFrame([{"foo": 5, "bar": 6}, {"foo": 7, "bar": 8}])
        dn.append(append_data_1)
        assert_frame_equal(dn.read(), pd.concat([original_data, append_data_1]).reset_index(drop=True))

    def test_sqlite_append_without_append_query_builder(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_pandas,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
        }

        dn = SQLDataNode("sqlite_dn", Scope.SCENARIO, properties=properties)
        with pytest.raises(MissingAppendQueryBuilder):
            dn.append(pd.DataFrame([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}]))

    def test_filter_pandas_exposed_type(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_pandas,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "pandas",
        }
        dn = SQLDataNode("foo", Scope.SCENARIO, properties=properties)
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
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_pandas,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "numpy",
        }
        dn = SQLDataNode("foo", Scope.SCENARIO, properties=properties)
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
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_pandas,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "numpy",
        }
        dn = SQLDataNode("foo", Scope.SCENARIO, properties=properties)

        # SQLDataNode.filter() should not call the MongoCollectionDataNode._read() method
        with patch.object(SQLDataNode, "_read") as read_mock:
            dn.filter(("foo", 1, Operator.EQUAL))
            dn.filter(("bar", 2, Operator.NOT_EQUAL))
            dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)

            assert read_mock["_read"].call_count == 0
