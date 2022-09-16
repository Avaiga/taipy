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
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from src.taipy.core.common.alias import DataNodeId
from src.taipy.core.data.sql import SQLDataNode
from src.taipy.core.exceptions.exceptions import InvalidExposedType, MissingRequiredProperty
from taipy.config.common.scope import Scope

if not util.find_spec("pyodbc"):
    pytest.skip("skipping tests because PyODBC is not installed", allow_module_level=True)


class MyCustomObject:
    def __init__(self, foo=None, bar=None, *args, **kwargs):
        self.foo = foo
        self.bar = bar
        self.args = args
        self.kwargs = kwargs


def my_write_query_builder(data: pd.DataFrame):
    insert_data = list(data.itertuples(index=False, name=None))
    return [
        "DELETE FROM foo",
        ("INSERT INTO foo VALUES (?,?)", insert_data)
    ]


def single_write_query_builder(data):
    return "DELETE FROM foo"


class TestSQLDataNode:
    __properties = [
        {
            "db_username": "sa",
            "db_password": "Passw0rd",
            "db_name": "taipy",
            "db_engine": "mssql",
            "read_query": "SELECT * FROM foo",
            "write_query_builder": my_write_query_builder,
            "db_extra_args": {
                "TrustServerCertificate": "yes",
            },
        },
        {
            "db_name": "taipy",
            "db_engine": "sqlite",
            "read_query": "SELECT * FROM foo",
            "write_query_builder": my_write_query_builder,
            "db_extra_args": {
                "TrustServerCertificate": "yes",
                "other": "value",
            },
        },
    ]

    @pytest.mark.parametrize("properties", __properties)
    def test_create(self, properties):
        dn = SQLDataNode(
            "foo_bar",
            Scope.PIPELINE,
            properties=properties,
        )
        assert isinstance(dn, SQLDataNode)
        assert dn.storage_type() == "sql"
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.parent_id is None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.exposed_type == "pandas"
        assert dn.read_query == "SELECT * FROM foo"
        assert dn.write_query_builder == my_write_query_builder

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
            SQLDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            SQLDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties=properties)

    def test_write_query_builder(self):
        dn = SQLDataNode(
            "foo_bar",
            Scope.PIPELINE,
            properties={
                "db_name": "taipy",
                "db_engine": "sqlite",
                "read_query": "SELECT * FROM foo",
                "write_query_builder": my_write_query_builder,
            },
        )
        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert engine_mock.mock_calls[4] == mock.call().__enter__().execute("DELETE FROM foo")
            assert engine_mock.mock_calls[5] == mock.call().__enter__().execute(
                "INSERT INTO foo VALUES (?,?)", [(1, 4), (2, 5), (3, 6)])

        dn = SQLDataNode(
            "foo_bar",
            Scope.PIPELINE,
            properties={
                "db_name": "taipy",
                "db_engine": "sqlite",
                "read_query": "SELECT * FROM foo",
                "write_query_builder": single_write_query_builder,
            },
        )
        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            # mock connection execute
            dn.write(pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]}))
            assert engine_mock.mock_calls[4] == mock.call().__enter__().execute("DELETE FROM foo")
