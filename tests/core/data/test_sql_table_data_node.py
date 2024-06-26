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

import pytest

from taipy.config import Config
from taipy.config.common.scope import Scope
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.sql_table import SQLTableDataNode
from taipy.core.exceptions.exceptions import InvalidExposedType, MissingRequiredProperty


class MyCustomObject:
    def __init__(self, foo=None, bar=None, *args, **kwargs):
        self.foo = foo
        self.bar = bar
        self.args = args
        self.kwargs = kwargs


class TestSQLTableDataNode:
    __sql_properties = [
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
        __sql_properties.append(
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
        __sql_properties.append(
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
        __sql_properties.append(
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

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_create(self, properties):
        sql_table_dn_config = Config.configure_sql_table_data_node("foo_bar", **properties)
        dn = _DataManagerFactory._build_manager()._create_and_set(sql_table_dn_config, None, None)
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

        sql_table_dn_config_1 = Config.configure_sql_table_data_node(
            "foo_bar", **properties, exposed_type=MyCustomObject
        )
        dn_1 = _DataManagerFactory._build_manager()._create_and_set(sql_table_dn_config_1, None, None)
        assert isinstance(dn_1, SQLTableDataNode)
        assert dn_1.exposed_type == MyCustomObject

    @pytest.mark.parametrize("properties", __sql_properties)
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
    @pytest.mark.parametrize("properties", __sql_properties)
    def test_modin_deprecated_in_favor_of_pandas(self, mock_read_as_pandas_dataframe, properties):
        properties["exposed_type"] = "modin"
        sql_data_node_as_modin = SQLTableDataNode("foo", Scope.SCENARIO, properties=properties)
        assert sql_data_node_as_modin.properties["exposed_type"] == "pandas"
        assert sql_data_node_as_modin.read() == "pandas"

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_raise_error_invalid_exposed_type(self, properties):
        custom_properties = properties.copy()
        custom_properties.pop("db_extra_args")
        custom_properties["exposed_type"] = "foo"
        with pytest.raises(InvalidExposedType):
            SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

    @pytest.mark.parametrize("properties", __sql_properties)
    @patch("pandas.read_sql_query")
    def test_engine_cache(self, _, properties):
        dn = SQLTableDataNode(
            "foo",
            Scope.SCENARIO,
            properties=properties,
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

            dn.write({})
            assert dn._engine is not None

            dn.some_random_attribute_that_does_not_related_to_engine = "foo"
            assert dn._engine is not None
