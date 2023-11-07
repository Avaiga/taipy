# Copyright 2023 Avaiga Private Limited
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
from unittest import mock

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
import pytest
from modin.pandas.test.utils import df_equals
from pandas.testing import assert_frame_equal

from src.taipy.core.data.data_node_id import DataNodeId
from src.taipy.core.data.operator import JoinOperator, Operator
from src.taipy.core.data.sql import SQLDataNode
from src.taipy.core.exceptions.exceptions import MissingRequiredProperty
from taipy.config.common.scope import Scope


class MyCustomObject:
    def __init__(self, foo=None, bar=None, *args, **kwargs):
        self.foo = foo
        self.bar = bar
        self.args = args
        self.kwargs = kwargs


def my_write_query_builder_with_pandas(data: pd.DataFrame):
    insert_data = data.to_dict("records")
    return ["DELETE FROM example", ("INSERT INTO example VALUES (:foo, :bar)", insert_data)]


def my_write_query_builder_with_modin(data: modin_pd.DataFrame):
    insert_data = data.to_dict("records")
    return ["DELETE FROM example", ("INSERT INTO example VALUES (:foo, :bar)", insert_data)]


def single_write_query_builder(data):
    return "DELETE FROM example"


class TestSQLDataNode:
    __pandas_properties = [
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

    __modin_properties = [
        {
            "db_name": "taipy.sqlite3",
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_modin,
            "exposed_type": "modin",
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
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_pandas,
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )
        __modin_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mssql",
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_modin,
                "exposed_type": "modin",
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
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_pandas,
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )
        __modin_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mysql",
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_modin,
                "exposed_type": "modin",
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
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_pandas,
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )
        __modin_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "postgresql",
                "read_query": "SELECT * FROM example",
                "write_query_builder": my_write_query_builder_with_modin,
                "exposed_type": "modin",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    @pytest.mark.parametrize("modin_properties", __modin_properties)
    def test_create(self, pandas_properties, modin_properties):
        dn = SQLDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties=pandas_properties,
        )
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

        dn = SQLDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties=modin_properties,
        )
        assert isinstance(dn, SQLDataNode)
        assert dn.storage_type() == "sql"
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.exposed_type == "modin"
        assert dn.read_query == "SELECT * FROM example"
        assert dn.write_query_builder == my_write_query_builder_with_modin

    @pytest.mark.parametrize("properties", __pandas_properties + __modin_properties)
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

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    @pytest.mark.parametrize("modin_properties", __modin_properties)
    def test_write_query_builder(self, pandas_properties, modin_properties):
        custom_properties = pandas_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLDataNode("foo_bar", Scope.SCENARIO, properties=custom_properties)
        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
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

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert len(engine_mock.mock_calls[4].args) == 1
            assert engine_mock.mock_calls[4].args[0].text == "DELETE FROM example"

        custom_properties = modin_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLDataNode("foo_bar", Scope.SCENARIO, properties=custom_properties)
        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(modin_pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
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

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(modin_pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
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

    def test_filter_modin_exposed_type(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM example",
            "write_query_builder": my_write_query_builder_with_modin,
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
            "exposed_type": "modin",
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
        assert dn[:2].equals(modin_pd.DataFrame([{"foo": 1, "bar": 1}, {"foo": 1, "bar": 2}]))

        # Test filter data
        filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
        filtered_by_indexing = dn[dn["foo"] == 1]
        expected_data = modin_pd.DataFrame([{"foo": 1, "bar": 1}, {"foo": 1, "bar": 2}, {"foo": 1, "bar": 3}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
        filtered_by_indexing = dn[dn["foo"] != 1]
        expected_data = modin_pd.DataFrame([{"foo": 2, "bar": 1}, {"foo": 2, "bar": 2}, {"foo": 2, "bar": 3}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
        filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
        expected_data = modin_pd.DataFrame(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 2, "bar": 1},
                {"foo": 2, "bar": 2},
            ]
        )
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

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
