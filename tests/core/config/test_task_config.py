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

import os
from unittest import mock

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core.config import DataNodeConfig
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def _configure_task_in_toml():
    return NamedTemporaryFile(
        content="""
[TAIPY]

[DATA_NODE.input]

[DATA_NODE.output]

[TASK.tasks1]
function = "builtins.print:function"
inputs = [ "input:SECTION",]
outputs = [ "output:SECTION",]
    """
    )


def _check_data_nodes_instance(dn_id, task_id):
    """Check if the data node instance in the task config correctly points to the Config._applied_config,
    not the Config._python_config or the Config._file_config
    """
    dn_config_applied_instance = Config.data_nodes[dn_id]
    for dn in Config.tasks[task_id].inputs:
        if dn.id == dn_id:
            dn_config_instance_via_task = dn
    for dn in Config.tasks[task_id].outputs:
        if dn.id == dn_id:
            dn_config_instance_via_task = dn

    dn_config_python_instance = None
    if Config._python_config._sections.get("DATA_NODE", None):
        dn_config_python_instance = Config._python_config._sections["DATA_NODE"][dn_id]

    dn_config_file_instance = None
    if Config._file_config._sections.get("DATA_NODE", None):
        dn_config_file_instance = Config._file_config._sections["DATA_NODE"][dn_id]

    if dn_config_python_instance:
        assert dn_config_python_instance.scope is None
    assert dn_config_python_instance is not dn_config_applied_instance
    assert dn_config_python_instance is not dn_config_instance_via_task

    if dn_config_file_instance:
        assert dn_config_file_instance.scope is None
    assert dn_config_file_instance is not dn_config_applied_instance
    assert dn_config_file_instance is not dn_config_instance_via_task

    assert dn_config_applied_instance.scope == DataNodeConfig._DEFAULT_SCOPE
    assert dn_config_instance_via_task is dn_config_applied_instance


def test_data_node_instance_when_configure_task_in_python():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")
    Config.configure_task("tasks1", print, input_config, output_config)

    _check_data_nodes_instance("input", "tasks1")
    _check_data_nodes_instance("output", "tasks1")


def test_data_node_instance_when_configure_task_by_loading_toml():
    toml_config = _configure_task_in_toml()
    Config.load(toml_config.filename)

    _check_data_nodes_instance("input", "tasks1")
    _check_data_nodes_instance("output", "tasks1")


def test_data_node_instance_when_configure_task_by_overriding_toml():
    toml_config = _configure_task_in_toml()
    Config.override(toml_config.filename)

    _check_data_nodes_instance("input", "tasks1")
    _check_data_nodes_instance("output", "tasks1")


def test_task_config_creation():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")
    task_config = Config.configure_task("tasks1", print, input_config, output_config)

    assert not task_config.skippable
    assert list(Config.tasks) == ["default", task_config.id]

    task2 = Config.configure_task("tasks2", print, input_config, output_config, skippable=True)
    assert task2.skippable
    assert list(Config.tasks) == ["default", task_config.id, task2.id]


def test_task_count():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")
    Config.configure_task("tasks1", print, input_config, output_config)
    assert len(Config.tasks) == 2

    Config.configure_task("tasks2", print, input_config, output_config)
    assert len(Config.tasks) == 3

    Config.configure_task("tasks3", print, input_config, output_config)
    assert len(Config.tasks) == 4


def test_task_getitem():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")
    task_id = "tasks1"
    task_cfg = Config.configure_task(task_id, print, input_config, output_config)

    assert Config.tasks[task_id].id == task_cfg.id
    assert Config.tasks[task_id].properties == task_cfg.properties
    assert Config.tasks[task_id].function == task_cfg.function
    assert Config.tasks[task_id].input_configs == task_cfg.input_configs
    assert Config.tasks[task_id].output_configs == task_cfg.output_configs
    assert Config.tasks[task_id].skippable == task_cfg.skippable


def test_task_creation_no_duplication():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")
    Config.configure_task("tasks1", print, input_config, output_config)

    assert len(Config.tasks) == 2

    Config.configure_task("tasks1", print, input_config, output_config)
    assert len(Config.tasks) == 2


def test_task_config_with_env_variable_value():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")

    with mock.patch.dict(os.environ, {"FOO": "plop", "BAR": "baz"}):
        Config.configure_task("task_name", print, input_config, output_config, prop="ENV[BAR]")
        assert Config.tasks["task_name"].prop == "baz"
        assert Config.tasks["task_name"].properties["prop"] == "baz"
        assert Config.tasks["task_name"]._properties["prop"] == "ENV[BAR]"


def test_clean_config():
    dn1 = Config.configure_data_node("dn1")
    dn2 = Config.configure_data_node("dn2")
    task1_config = Config.configure_task("id1", print, dn1, dn2)
    task2_config = Config.configure_task("id2", print, dn2, dn1)

    assert Config.tasks["id1"] is task1_config
    assert Config.tasks["id2"] is task2_config

    task1_config._clean()
    task2_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.tasks["id1"] is task1_config
    assert Config.tasks["id2"] is task2_config

    assert task1_config.id == "id1"
    assert task2_config.id == "id2"
    assert task1_config.function is task1_config.function is None
    assert task1_config.inputs == task1_config.inputs == []
    assert task1_config.input_configs == task1_config.input_configs == []
    assert task1_config.outputs == task1_config.outputs == []
    assert task1_config.output_configs == task1_config.output_configs == []
    assert task1_config.skippable is task1_config.skippable is False
    assert task1_config.properties == task1_config.properties == {}


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
