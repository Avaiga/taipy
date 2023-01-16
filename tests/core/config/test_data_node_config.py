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

import os
from datetime import datetime
from unittest import mock

import pytest

from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.config import DataNodeConfig
from src.taipy.core.config.job_config import JobConfig
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import ConfigurationIssueError, ConfigurationUpdateBlocked


def test_data_node_config_check():
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

    with pytest.raises(ConfigurationIssueError):
        Config.configure_data_node("data_nodes", storage_type="bar")
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.configure_data_node("data_nodes", scope="bar")
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.configure_data_node("data_nodes", storage_type="sql")
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.configure_data_node("data_nodes", storage_type="generic")
        Config.check()


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
        my_property=datetime(1991, 1, 1),
        foo="hello",
        test=1,
        test_dict={"type": "Datetime", 2: "daw"},
    )
    assert data_node_config.foo == "hello"
    assert data_node_config.my_property == datetime(1991, 1, 1)
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


def test_data_node_with_env_variable_in_write_fct_params():
    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        Config.configure_data_node(
            "data_node", storage_type="generic", write_fct_params=["ENV[FOO]", "my_param", "ENV[BAZ]"]
        )
        assert Config.data_nodes["data_node"].write_fct_params == ["bar", "my_param", "qux"]


def test_data_node_with_env_variable_in_read_fct_params():
    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        Config.configure_data_node(
            "data_node", storage_type="generic", read_fct_params=["ENV[FOO]", "my_param", "ENV[BAZ]"]
        )
        assert Config.data_nodes["data_node"].read_fct_params == ["bar", "my_param", "qux"]


def test_block_datanode_config_update_in_development_mode():
    data_node_id = "data_node_id"
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    data_node_config = Config.configure_data_node(
        id=data_node_id,
        storage_type="pickle",
        default_path="foo.p",
        scope=Scope.SCENARIO,
        cacheable=False,
    )

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].cacheable is False
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}

    _SchedulerFactory._build_dispatcher()

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.storage_type = "foo"

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.scope = Scope.PIPELINE

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.cacheable = True

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.properties = {"foo": "bar"}

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].cacheable is False
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}


def test_block_datanode_config_update_in_standalone_mode():
    data_node_id = "data_node_id"
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    data_node_config = Config.configure_data_node(
        id=data_node_id,
        storage_type="pickle",
        default_path="foo.p",
        scope=Scope.SCENARIO,
        cacheable=False,
    )

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].cacheable is False
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}

    _SchedulerFactory._build_dispatcher()

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.storage_type = "foo"

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.scope = Scope.PIPELINE

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.cacheable = True

    with pytest.raises(ConfigurationUpdateBlocked):
        data_node_config.properties = {"foo": "bar"}

    assert Config.data_nodes[data_node_id].id == data_node_id
    assert Config.data_nodes[data_node_id].default_path == "foo.p"
    assert Config.data_nodes[data_node_id].storage_type == "pickle"
    assert Config.data_nodes[data_node_id].scope == Scope.SCENARIO
    assert Config.data_nodes[data_node_id].cacheable is False
    assert Config.data_nodes[data_node_id].properties == {"default_path": "foo.p"}
