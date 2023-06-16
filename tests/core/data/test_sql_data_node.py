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
import pandas as pd
import pytest

from src.taipy.core.data.data_node_id import DataNodeId
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
    insert_data = list(data.itertuples(index=False, name=None))
    return ["DELETE FROM foo", ("INSERT INTO foo VALUES (?,?)", insert_data)]


def my_write_query_builder_with_modin(data: modin_pd.DataFrame):
    insert_data = list(data.itertuples(index=False, name=None))
    return ["DELETE FROM foo", ("INSERT INTO foo VALUES (?,?)", insert_data)]


def single_write_query_builder(data):
    return "DELETE FROM foo"


class TestSQLDataNode:
    __pandas_properties = [
        {
            "db_name": "taipy.sqlite3",
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM foo",
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
            "read_query": "SELECT * FROM foo",
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
                "read_query": "SELECT * FROM foo",
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
                "read_query": "SELECT * FROM foo",
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
                "read_query": "SELECT * FROM foo",
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
                "read_query": "SELECT * FROM foo",
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
                "read_query": "SELECT * FROM foo",
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
                "read_query": "SELECT * FROM foo",
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
            Scope.PIPELINE,
            properties=pandas_properties,
        )
        assert isinstance(dn, SQLDataNode)
        assert dn.storage_type() == "sql"
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.exposed_type == "pandas"
        assert dn.read_query == "SELECT * FROM foo"
        assert dn.write_query_builder == my_write_query_builder_with_pandas

        dn = SQLDataNode(
            "foo_bar",
            Scope.PIPELINE,
            properties=modin_properties,
        )
        assert isinstance(dn, SQLDataNode)
        assert dn.storage_type() == "sql"
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.exposed_type == "modin"
        assert dn.read_query == "SELECT * FROM foo"
        assert dn.write_query_builder == my_write_query_builder_with_modin

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
            SQLDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            SQLDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties=properties)

    @pytest.mark.parametrize("pandas_properties", __pandas_properties)
    @pytest.mark.parametrize("modin_properties", __pandas_properties)
    def test_write_query_builder(self, pandas_properties, modin_properties):
        custom_properties = pandas_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLDataNode("foo_bar", Scope.PIPELINE, properties=custom_properties)
        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert engine_mock.mock_calls[4] == mock.call().__enter__().execute("DELETE FROM foo")
            assert engine_mock.mock_calls[5] == mock.call().__enter__().execute(
                "INSERT INTO foo VALUES (?,?)", [(1, 4), (2, 5), (3, 6)]
            )

        custom_properties["write_query_builder"] = single_write_query_builder
        dn = SQLDataNode("foo_bar", Scope.PIPELINE, properties=custom_properties)

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert engine_mock.mock_calls[4] == mock.call().__enter__().execute("DELETE FROM foo")

        custom_properties = modin_properties.copy()
        custom_properties.pop("db_extra_args")
        dn = SQLDataNode("foo_bar", Scope.PIPELINE, properties=custom_properties)
        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(modin_pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert engine_mock.mock_calls[4] == mock.call().__enter__().execute("DELETE FROM foo")
            assert engine_mock.mock_calls[5] == mock.call().__enter__().execute(
                "INSERT INTO foo VALUES (?,?)", [(1, 4), (2, 5), (3, 6)]
            )

        custom_properties["write_query_builder"] = single_write_query_builder
        dn = SQLDataNode("foo_bar", Scope.PIPELINE, properties=custom_properties)

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(modin_pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert engine_mock.mock_calls[4] == mock.call().__enter__().execute("DELETE FROM foo")

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

        dn = SQLDataNode("sqlite_dn", Scope.PIPELINE, properties=properties)
        data = dn.read()
        assert data.equals(pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]))
