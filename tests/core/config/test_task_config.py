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
from unittest import mock

from taipy.config.config import Config


def test_task_config_creation():
    input_config = Config.configure_data_node("input")
    output_config = Config.configure_data_node("output")
    task_config = Config.configure_task("tasks1", print, input_config, output_config)

    assert list(Config.tasks) == ["default", task_config.id]

    task2 = Config.configure_task("tasks2", print, input_config, output_config)
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
