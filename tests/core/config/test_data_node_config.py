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

import datetime
import os
from unittest import mock

import pytest

from taipy.common.config import Config
from taipy.common.config.common.scope import Scope
from taipy.common.config.exceptions.exceptions import ConfigurationUpdateBlocked
from taipy.core import MongoDefaultDocument
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config import DataNodeConfig
from taipy.core.config.job_config import JobConfig


def test_data_node_config_default_parameter():
    csv_dn_cfg = Config.configure_data_node("data_node_1", "csv")
    assert csv_dn_cfg.scope == Scope.SCENARIO
    assert csv_dn_cfg.has_header is True
    assert csv_dn_cfg.exposed_type == "pandas"
    assert csv_dn_cfg.validity_period is None

    json_dn_cfg = Config.configure_data_node("data_node_2", "json")
    assert json_dn_cfg.scope == Scope.SCENARIO
    assert json_dn_cfg.validity_period is None

    parquet_dn_cfg = Config.configure_data_node("data_node_3", "parquet")
    assert parquet_dn_cfg.scope == Scope.SCENARIO
    assert parquet_dn_cfg.engine == "pyarrow"
    assert parquet_dn_cfg.compression == "snappy"
    assert parquet_dn_cfg.exposed_type == "pandas"
    assert parquet_dn_cfg.validity_period is None

    excel_dn_cfg = Config.configure_data_node("data_node_4", "excel")
    assert excel_dn_cfg.scope == Scope.SCENARIO
    assert excel_dn_cfg.has_header is True
    assert excel_dn_cfg.exposed_type == "pandas"
    assert excel_dn_cfg.validity_period is None

    generic_dn_cfg = Config.configure_data_node("data_node_5", "generic")
    assert generic_dn_cfg.scope == Scope.SCENARIO
    assert generic_dn_cfg.validity_period is None

    in_memory_dn_cfg = Config.configure_data_node("data_node_6", "in_memory")
    assert in_memory_dn_cfg.scope == Scope.SCENARIO
    assert in_memory_dn_cfg.validity_period is None

    pickle_dn_cfg = Config.configure_data_node("data_node_7", "pickle")
    assert pickle_dn_cfg.scope == Scope.SCENARIO
    assert pickle_dn_cfg.validity_period is None

    sql_table_dn_cfg = Config.configure_data_node(
        "data_node_8", "sql_table", db_name="test", db_engine="mssql", table_name="test"
    )
    assert sql_table_dn_cfg.scope == Scope.SCENARIO
    assert sql_table_dn_cfg.db_host == "localhost"
    assert sql_table_dn_cfg.db_port == 1433
    assert sql_table_dn_cfg.db_driver == ""
    assert sql_table_dn_cfg.sqlite_file_extension == ".db"
    assert sql_table_dn_cfg.exposed_type == "pandas"
    assert sql_table_dn_cfg.validity_period is None

    sql_dn_cfg = Config.configure_data_node(
        "data_node_9", "sql", db_name="test", db_engine="mssql", read_query="test", write_query_builder=print
    )
    assert sql_dn_cfg.scope == Scope.SCENARIO
    assert sql_dn_cfg.db_host == "localhost"
    assert sql_dn_cfg.db_port == 1433
    assert sql_dn_cfg.db_driver == ""
    assert sql_dn_cfg.sqlite_file_extension == ".db"
    assert sql_dn_cfg.exposed_type == "pandas"
    assert sql_dn_cfg.validity_period is None

    mongo_dn_cfg = Config.configure_data_node(
        "data_node_10", "mongo_collection", db_name="test", collection_name="test"
    )
    assert mongo_dn_cfg.scope == Scope.SCENARIO
    assert mongo_dn_cfg.db_host == "localhost"
    assert mongo_dn_cfg.db_port == 27017
    assert mongo_dn_cfg.custom_document == MongoDefaultDocument
    assert mongo_dn_cfg.db_username == ""
    assert mongo_dn_cfg.db_password == ""
    assert mongo_dn_cfg.db_driver == ""
    assert mongo_dn_cfg.validity_period is None

    aws_s3_object_dn_cfg = Config.configure_data_node(
        "data_node_11",
        "s3_object",
        aws_access_key="test",
        aws_secret_access_key="test_secret",
        aws_s3_bucket_name="test_bucket",
        aws_s3_object_key="test_file.txt",
    )
    assert aws_s3_object_dn_cfg.scope == Scope.SCENARIO
    assert aws_s3_object_dn_cfg.aws_access_key == "test"
    assert aws_s3_object_dn_cfg.aws_secret_access_key == "test_secret"
    assert aws_s3_object_dn_cfg.aws_s3_bucket_name == "test_bucket"
    assert aws_s3_object_dn_cfg.aws_s3_object_key == "test_file.txt"
    assert aws_s3_object_dn_cfg.aws_region is None
    assert aws_s3_object_dn_cfg.aws_s3_object_parameters is None
    assert aws_s3_object_dn_cfg.validity_period is None


def test_data_node_config_check(caplog):
    data_node_config = Config.configure_data_node("data_nodes1", "pickle")
    assert list(Config.data_nodes) == [DataNodeConfig._DEFAULT_KEY, data_node_config.id]

    data_node2_config = Config.configure_data_node("data_nodes2", "pickle")
    assert list(Config.data_nodes) == [DataNodeConfig._DEFAULT_KEY, data_node_config.id, data_node2_config.id]

    data_node3_config = Config.configure_data_node("data_nodes3", "csv", has_header=True, default_path="")
    assert list(Config.data_nodes) == [
        "default",
        data_node_config.id,
        data_node2_config.id,
        data_node3_config.id,
    ]

    with pytest.raises(SystemExit):
        Config.configure_data_node("data_nodes", storage_type="bar")
        Config.check()
    expected_error_message = (
        "`storage_type` field of DataNodeConfig `data_nodes` must be either csv, sql_table,"
        " sql, mongo_collection, pickle, excel, generic, json, parquet, s3_object, or in_memory. Current"
        ' value of property `storage_type` is "bar".'
    )
    assert expected_error_message in caplog.text

    with pytest.raises(SystemExit):
        Config.configure_data_node("data_nodes", scope="bar")
        Config.check()
    expected_error_message = (
        "`scope` field of DataNodeConfig `data_nodes` must be populated with a Scope value."
        ' Current value of property `scope` is "bar".'
    )
    assert expected_error_message in caplog.text

    with pytest.raises(TypeError):
        Config.configure_data_node("data_nodes", storage_type="sql")

    with pytest.raises(SystemExit):
        Config.configure_data_node("data_nodes", storage_type="generic")
        Config.check()
    expected_error_message = (
        "`storage_type` field of DataNodeConfig `data_nodes` must be either csv, sql_table,"
        " sql, mongo_collection, pickle, excel, generic, json, parquet, s3_object, or in_memory."
        ' Current value of property `storage_type` is "bar".'
    )
    assert expected_error_message in caplog.text


def test_configure_data_node_from_another_configuration():
    d1_cfg = Config.configure_sql_table_data_node(
        "d1",
        db_username="foo",
        db_password="bar",
        db_name="db",
        db_engine="mssql",
        db_port=8080,
        db_host="somewhere",
        table_name="foo",
        scope=Scope.GLOBAL,
        foo="bar",
    )

    d2_cfg = Config.configure_data_node_from(
        source_configuration=d1_cfg,
        id="d2",
        table_name="table_2",
    )

    assert d2_cfg.id == "d2"
    assert d2_cfg.storage_type == "sql_table"
    assert d2_cfg.scope == Scope.GLOBAL
    assert d2_cfg.validity_period is None
    assert d2_cfg.db_username == "foo"
    assert d2_cfg.db_password == "bar"
    assert d2_cfg.db_name == "db"
    assert d2_cfg.db_engine == "mssql"
    assert d2_cfg.db_port == 8080
    assert d2_cfg.db_host == "somewhere"
    assert d2_cfg.table_name == "table_2"
    assert d2_cfg.foo == "bar"

    d3_cfg = Config.configure_data_node_from(
        source_configuration=d1_cfg,
        id="d3",
        scope=Scope.SCENARIO,
        validity_period=datetime.timedelta(days=1),
        table_name="table_3",
        foo="baz",
    )

    assert d3_cfg.id == "d3"
    assert d3_cfg.storage_type == "sql_table"
    assert d3_cfg.scope == Scope.SCENARIO
    assert d3_cfg.validity_period == datetime.timedelta(days=1)
    assert d3_cfg.db_username == "foo"
    assert d3_cfg.db_password == "bar"
    assert d3_cfg.db_name == "db"
    assert d3_cfg.db_engine == "mssql"
    assert d3_cfg.db_port == 8080
    assert d3_cfg.db_host == "somewhere"
    assert d3_cfg.table_name == "table_3"
    assert d3_cfg.foo == "baz"


def test_data_node_count():
    Config.configure_data_node("data_nodes1", "pickle")
    assert len(Config.data_nodes) == 2

    Config.configure_data_node("data_nodes2", "pickle")
    assert len(Config.data_nodes) == 3

    Config.configure_data_node("data_nodes3", "pickle")
    assert len(Config.data_nodes) == 4


def test_data_node_getitem():
    data_node_id = "data_nodes1"
    data_node_config = Config.configure_data_node(data_node_id, "pickle", default_path="foo.p")

    assert Config.data_nodes[data_node_id].id == data_node_config.id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == data_node_config.storage_type
    assert Config.data_nodes[data_node_id].scope == data_node_config.scope
    assert Config.data_nodes[data_node_id].properties == data_node_config.properties
    assert Config.data_nodes[data_node_id].cacheable == data_node_config.cacheable


def test_data_node_creation_no_duplication():
    Config.configure_data_node("data_nodes1", "pickle")

    assert len(Config.data_nodes) == 2

    Config.configure_data_node("data_nodes1", "pickle")
    assert len(Config.data_nodes) == 2


def test_date_node_create_with_datetime():
    data_node_config = Config.configure_data_node(
        id="datetime_data",
        my_property=datetime.datetime(1991, 1, 1),
        foo="hello",
        test=1,
        test_dict={"type": "Datetime", 2: "daw"},
    )
    assert data_node_config.foo == "hello"
    assert data_node_config.my_property == datetime.datetime(1991, 1, 1)
    assert data_node_config.test == 1
    assert data_node_config.test_dict.get("type") == "Datetime"


def test_data_node_with_env_variable_value():
    with mock.patch.dict(os.environ, {"FOO": "pickle", "BAR": "baz"}):
        Config.configure_data_node("data_node", storage_type="ENV[FOO]", prop="ENV[BAR]")
        assert Config.data_nodes["data_node"].prop == "baz"
        assert Config.data_nodes["data_node"].properties["prop"] == "baz"
        assert Config.data_nodes["data_node"]._properties["prop"] == "ENV[BAR]"
        assert Config.data_nodes["data_node"].storage_type == "pickle"
        assert Config.data_nodes["data_node"]._storage_type == "ENV[FOO]"


def test_data_node_with_env_variable_in_write_fct_args():
    def read_fct(): ...

    def write_fct(): ...

    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        Config.configure_data_node(
            "data_node",
            storage_type="generic",
            read_fct=read_fct,
            write_fct=write_fct,
            write_fct_args=["ENV[FOO]", "my_param", "ENV[BAZ]"],
        )
        assert Config.data_nodes["data_node"].write_fct_args == ["bar", "my_param", "qux"]


def test_data_node_with_env_variable_in_read_fct_args():
    def read_fct(): ...

    def write_fct(): ...

    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        Config.configure_data_node(
            "data_node",
            storage_type="generic",
            read_fct=read_fct,
            write_fct=write_fct,
            read_fct_args=["ENV[FOO]", "my_param", "ENV[BAZ]"],
        )
        assert Config.data_nodes["data_node"].read_fct_args == ["bar", "my_param", "qux"]


def test_block_datanode_config_update_in_development_mode():
    data_node_id = "data_node_id"
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    data_node_config = Config.configure_data_node(
        id=data_node_id,
        storage_type="pickle",
        default_path="foo.p",
        scope=Scope.SCENARIO,
    )

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}

    _OrchestratorFactory._build_dispatcher()

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.storage_type = "foo"

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.scope = Scope.SCENARIO

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.cacheable = True

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.properties = {"foo": "bar"}

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}


def test_block_datanode_config_update_in_standalone_mode():
    data_node_id = "data_node_id"
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    data_node_config = Config.configure_data_node(
        id=data_node_id,
        storage_type="pickle",
        default_path="foo.p",
        scope=Scope.SCENARIO,
    )

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}

    _OrchestratorFactory._build_dispatcher()

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.storage_type = "foo"

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.scope = Scope.SCENARIO

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.cacheable = True

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.properties = {"foo": "bar"}

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}


def test_clean_config():
    dn1_config = Config.configure_data_node(
        id="id1",
        storage_type="csv",
        default_path="foo.p",
        scope=Scope.GLOBAL,
        validity_period=datetime.timedelta(2),
    )
    dn2_config = Config.configure_data_node(
        id="id2",
        storage_type="json",
        default_path="bar.json",
        scope=Scope.GLOBAL,
        validity_period=datetime.timedelta(2),
    )

    assert Config.data_nodes["id1"] is dn1_config
    assert Config.data_nodes["id2"] is dn2_config

    dn1_config._clean()
    dn2_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.data_nodes["id1"] is dn1_config
    assert Config.data_nodes["id2"] is dn2_config

    # Check if the value is similar to the default_config, but with difference instances
    assert dn1_config.id == "id1"
    assert dn2_config.id == "id2"
    assert dn1_config.storage_type == dn2_config.storage_type == "pickle"
    assert dn1_config.scope == dn2_config.scope == Scope.SCENARIO
    assert dn1_config.validity_period is dn2_config.validity_period is None
    assert dn1_config.default_path is dn2_config.default_path is None
    assert dn1_config.properties == dn2_config.properties == {}


def test_deprecated_cacheable_attribute_remains_compatible():
    dn_1_id = "dn_1_id"
    dn_1_config = Config.configure_data_node(
        id=dn_1_id,
        storage_type="pickle",
        cacheable=False,
        scope=Scope.SCENARIO,
    )
    assert Config.data_nodes[dn_1_id].id == dn_1_id
    assert Config.data_nodes[dn_1_id].storage_type == "pickle"
    assert Config.data_nodes[dn_1_id].scope == Scope.SCENARIO
    assert Config.data_nodes[dn_1_id].properties == {"cacheable": False}
    assert not Config.data_nodes[dn_1_id].cacheable
    dn_1_config.cacheable = True
    assert Config.data_nodes[dn_1_id].properties == {"cacheable": True}
    assert Config.data_nodes[dn_1_id].cacheable

    dn_2_id = "dn_2_id"
    dn_2_config = Config.configure_data_node(
        id=dn_2_id,
        storage_type="pickle",
        cacheable=True,
        scope=Scope.SCENARIO,
    )
    assert Config.data_nodes[dn_2_id].id == dn_2_id
    assert Config.data_nodes[dn_2_id].storage_type == "pickle"
    assert Config.data_nodes[dn_2_id].scope == Scope.SCENARIO
    assert Config.data_nodes[dn_2_id].properties == {"cacheable": True}
    assert Config.data_nodes[dn_2_id].cacheable
    dn_2_config.cacheable = False
    assert Config.data_nodes[dn_1_id].properties == {"cacheable": False}
    assert not Config.data_nodes[dn_1_id].cacheable

    dn_3_id = "dn_3_id"
    dn_3_config = Config.configure_data_node(
        id=dn_3_id,
        storage_type="pickle",
        scope=Scope.SCENARIO,
    )
    assert Config.data_nodes[dn_3_id].id == dn_3_id
    assert Config.data_nodes[dn_3_id].storage_type == "pickle"
    assert Config.data_nodes[dn_3_id].scope == Scope.SCENARIO
    assert Config.data_nodes[dn_3_id].properties == {}
    assert not Config.data_nodes[dn_3_id].cacheable
    dn_3_config.cacheable = True
    assert Config.data_nodes[dn_3_id].properties == {"cacheable": True}
    assert Config.data_nodes[dn_3_id].cacheable
