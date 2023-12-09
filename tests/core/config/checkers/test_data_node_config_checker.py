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

from copy import copy
from datetime import timedelta

import pytest

from taipy.config import Config
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.scope import Scope
from taipy.core.config.data_node_config import DataNodeConfig


class MyCustomClass:
    pass


class TestDataNodeConfigChecker:
    def test_check_config_id(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])
        config._sections[DataNodeConfig.name]["new"].id = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "config_id of DataNodeConfig `None` is empty." in caplog.text

        config._sections[DataNodeConfig.name]["new"].id = "new"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

    def test_check_if_entity_property_key_used_is_predefined(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])
        config._sections[DataNodeConfig.name]["new"]._properties["_entity_owner"] = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "Properties of DataNodeConfig `default` cannot have `_entity_owner` as its property." in caplog.text

        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])
        config._sections[DataNodeConfig.name]["new"]._properties["_entity_owner"] = "entity_owner"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "Properties of DataNodeConfig `default` cannot have `_entity_owner` as its property."
            ' Current value of property `_entity_owner` is "entity_owner".'
        )
        assert expected_error_message in caplog.text

    def test_check_storage_type(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])

        config._sections[DataNodeConfig.name]["new"].storage_type = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`storage_type` field of DataNodeConfig `new` must be either csv, sql_table,"
            " sql, mongo_collection, pickle, excel, generic, json, parquet, s3_object, or in_memory."
            ' Current value of property `storage_type` is "bar".'
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["new"].storage_type = "csv"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "excel"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "pickle"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "json"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "parquet"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "in_memory"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messages = [
            "Either `read_fct` field or `write_fct` field of DataNodeConfig `new` "
            "must be populated with a Callable function.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "sql_table"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 3
        expected_error_messages = [
            "DataNodeConfig `new` is missing the required property `db_name` for type `sql_table`.",
            "DataNodeConfig `new` is missing the required property `db_engine` for type `sql_table`.",
            "DataNodeConfig `new` is missing the required property `table_name` for type `sql_table`.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "sql"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 4
        expected_error_messages = [
            "DataNodeConfig `new` is missing the required property `db_name` for type `sql`.",
            "DataNodeConfig `new` is missing the required property `db_engine` for type `sql`.",
            "DataNodeConfig `new` is missing the required property `read_query` for type `sql`.",
            "DataNodeConfig `new` is missing the required property `write_query_builder` for type `sql`.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "mongo_collection"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        expected_error_messages = [
            "DataNodeConfig `new` is missing the required property `db_name` for type `mongo_collection`.",
            "DataNodeConfig `new` is missing the required property `collection_name` for type `mongo_collection`.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "s3_object"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 4
        expected_error_messages = [
            "DataNodeConfig `new` is missing the required property `aws_access_key` for type `s3_object`.",
            "DataNodeConfig `new` is missing the required property `aws_secret_access_key` for type `s3_object`.",
            "DataNodeConfig `new` is missing the required property `aws_s3_bucket_name` for type `s3_object`.",
            "DataNodeConfig `new` is missing the required property `aws_s3_object_key` for type `s3_object`.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

    def test_check_properties_of_sqlite_engine(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])

        # Test SQLite engine
        config._sections[DataNodeConfig.name]["new"].storage_type = "sql_table"
        config._sections[DataNodeConfig.name]["new"].properties = {"db_engine": "sqlite"}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        expected_error_messages = [
            "DataNodeConfig `new` is missing the required property `db_name` for type `sql_table`.",
            "DataNodeConfig `new` is missing the required property `table_name` for type `sql_table`.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

    def test_check_properties_of_not_sqlite_engine(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])

        # Test other engines
        config._sections[DataNodeConfig.name]["new"].storage_type = "sql_table"
        config._sections[DataNodeConfig.name]["new"].properties = {"db_engine": "mssql"}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 4

        config._sections[DataNodeConfig.name]["new"].storage_type = "sql_table"
        config._sections[DataNodeConfig.name]["new"].properties = {"db_engine": "mysql"}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 4

        config._sections[DataNodeConfig.name]["new"].storage_type = "sql_table"
        config._sections[DataNodeConfig.name]["new"].properties = {"db_engine": "postgresql"}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 4

        expected_error_messages = [
            "DataNodeConfig `new` is missing the required property `db_username` for type `sql_table`.",
            "DataNodeConfig `new` is missing the required property `db_password` for type `sql_table`.",
            "DataNodeConfig `new` is missing the required property `db_name` for type `sql_table`.",
            "DataNodeConfig `new` is missing the required property `table_name` for type `sql_table`.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

    def test_check_scope(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        config._sections[DataNodeConfig.name]["default"].scope = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`scope` field of DataNodeConfig `default` must be populated with a Scope"
            ' value. Current value of property `scope` is "bar".'
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["default"].scope = 1
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`scope` field of DataNodeConfig `default` must be populated with a Scope"
            " value. Current value of property `scope` is 1."
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["default"].scope = Scope.GLOBAL
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[DataNodeConfig.name]["default"].scope = Scope.CYCLE
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[DataNodeConfig.name]["default"].scope = Scope.SCENARIO
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

    def test_check_validity_period(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        config._sections[DataNodeConfig.name]["default"].validity_period = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`validity_period` field of DataNodeConfig `default` must be None or populated with"
            ' a timedelta value. Current value of property `validity_period` is "bar".'
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["default"].validity_period = 1
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`validity_period` field of DataNodeConfig `default` must be None or populated with"
            " a timedelta value. Current value of property `validity_period` is 1."
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["default"].validity_period = None
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[DataNodeConfig.name]["default"].validity_period = timedelta(1)
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

    def test_check_required_properties(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])

        config._sections[DataNodeConfig.name]["new"].storage_type = "csv"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "csv"
        config._sections[DataNodeConfig.name]["new"].properties = {"has_header": True}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "csv"
        config._sections[DataNodeConfig.name]["new"].properties = {"path": "bar"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        required_properties = ["db_username", "db_password", "db_name", "db_engine", "table_name"]
        config._sections[DataNodeConfig.name]["new"].storage_type = "sql_table"
        config._sections[DataNodeConfig.name]["new"].properties = {key: f"the_{key}" for key in required_properties}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "sql"
        config._sections[DataNodeConfig.name]["new"].properties = {
            "db_username": "foo",
            "db_password": "foo",
            "db_name": "foo",
            "db_engine": "foo",
            "read_query": "foo",
            "write_query_builder": print,
        }
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "mongo_collection"
        config._sections[DataNodeConfig.name]["new"].properties = {"db_name": "foo", "collection_name": "bar"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "s3_object"
        config._sections[DataNodeConfig.name]["new"].properties = {
            "aws_access_key": "access_key",
            "aws_secret_access_key": "secret_acces_key",
            "aws_s3_bucket_name": "s3_bucket_name",
            "aws_s3_object_key": "s3_object_key",
        }
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "excel"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "excel"
        config._sections[DataNodeConfig.name]["new"].properties = {"has_header": True}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "excel"
        config._sections[DataNodeConfig.name]["new"].properties = {"path": "bar"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "excel"
        config._sections[DataNodeConfig.name]["new"].properties = {
            "has_header": True,
            "path": "bar",
            "sheet_name": ["sheet_name_1", "sheet_name_2"],
        }
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"read_fct": print}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": print}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": print, "read_fct": print}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "json"
        config._sections[DataNodeConfig.name]["new"].properties = {"default_path": "bar"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

    def test_required_properties_on_default_only_raise_warning(self):
        config = Config._applied_config
        Config._compile_configs()
        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])

        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1

    def test_check_callable_properties(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        config._sections[DataNodeConfig.name]["new"] = copy(config._sections[DataNodeConfig.name]["default"])

        config._sections[DataNodeConfig.name]["new"].storage_type = "sql"
        config._sections[DataNodeConfig.name]["new"].properties = {
            "db_username": "foo",
            "db_password": "foo",
            "db_name": "foo",
            "db_engine": "foo",
            "read_query": "foo",
            "write_query_builder": 1,
            "append_query_builder": 2,
        }
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        expected_error_message_1 = (
            "`write_query_builder` of DataNodeConfig `new` must be populated with a Callable function."
            " Current value of property `write_query_builder` is 1."
        )
        assert expected_error_message_1 in caplog.text
        expected_error_message_2 = (
            "`append_query_builder` of DataNodeConfig `new` must be populated with a Callable function."
            " Current value of property `append_query_builder` is 2."
        )
        assert expected_error_message_2 in caplog.text

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": 12}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messages = [
            "`write_fct` of DataNodeConfig `new` must be populated with a Callable function. Current value"
            " of property `write_fct` is 12.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"read_fct": 5}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_messages = [
            "`read_fct` of DataNodeConfig `new` must be populated with a Callable function. Current value"
            " of property `read_fct` is 5.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": 9, "read_fct": 5}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        expected_error_messages = [
            "`write_fct` of DataNodeConfig `new` must be populated with a Callable function. Current value"
            " of property `write_fct` is 9.",
            "`read_fct` of DataNodeConfig `new` must be populated with a Callable function. Current value"
            " of property `read_fct` is 5.",
        ]
        assert all(message in caplog.text for message in expected_error_messages)

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": print, "read_fct": 5}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": 5, "read_fct": print}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1

        config._sections[DataNodeConfig.name]["new"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["new"].properties = {"write_fct": print, "read_fct": print}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

    def test_check_read_write_fct_args(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["default"].properties = {"write_fct": print, "read_fct": print}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["default"].properties = {
            "write_fct": print,
            "read_fct": print,
            "write_fct_args": "foo",
        }
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`write_fct_args` field of DataNodeConfig `default` must be populated with a List value."
            ' Current value of property `write_fct_args` is "foo".'
        )
        assert expected_error_message in caplog.text
        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["default"].properties = {
            "write_fct": print,
            "read_fct": print,
            "write_fct_args": list("foo"),
        }
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["default"].properties = {
            "write_fct": print,
            "read_fct": print,
            "read_fct_args": 1,
        }
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "`read_fct_args` field of DataNodeConfig `default` must be populated with a List value."
            " Current value of property `read_fct_args` is 1."
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["default"].properties = {
            "write_fct": print,
            "read_fct": print,
            "read_fct_args": list("foo"),
        }
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["default"].storage_type = "generic"
        config._sections[DataNodeConfig.name]["default"].properties = {
            "write_fct": print,
            "read_fct": print,
            "write_fct_args": ["foo"],
            "read_fct_args": ["foo"],
        }
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

    def test_check_exposed_types(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        config._sections[DataNodeConfig.name]["default"].storage_type = "csv"
        config._sections[DataNodeConfig.name]["default"].properties = {"exposed_type": "foo"}
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            'The `exposed_type` of DataNodeConfig `default` must be either "pandas", "modin"'
            ', "numpy", or a custom type. Current value of property `exposed_type` is "foo".'
        )
        assert expected_error_message in caplog.text

        config._sections[DataNodeConfig.name]["default"].properties = {"exposed_type": "pandas"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["default"].properties = {"exposed_type": "modin"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["default"].properties = {"exposed_type": "numpy"}
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[DataNodeConfig.name]["default"].properties = {"exposed_type": MyCustomClass}
        Config.check()
        assert len(Config._collector.errors) == 0
