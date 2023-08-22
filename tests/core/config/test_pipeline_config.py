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

import os
from unittest import mock

import pytest

from taipy.config.config import Config
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def _configure_sequence_in_toml():
    return NamedTemporaryFile(
        content="""
[TAIPY]

[TASK.task1]
function = "builtins.print:function"
inputs = []
outputs = []

[TASK.task2]
function = "builtins.print:function"
inputs = []
outputs = []

[SEQUENCE.sequences1]
tasks = [ "task1:SECTION", "task2:SECTION"]
    """
    )


def _check_tasks_instance(task_id, sequence_id):
    """Check if the task instance in the sequence config correctly points to the Config._applied_config,
    not the Config._python_config or the Config._file_config
    """
    task_config_applied_instance = Config.tasks[task_id]
    for task in Config.sequences[sequence_id].tasks:
        if task.id == task_id:
            task_config_instance_via_sequence = task

    task_config_python_instance = None
    if Config._python_config._sections.get("TASK", None):
        task_config_python_instance = Config._python_config._sections["TASK"][task_id]

    task_config_file_instance = None
    if Config._file_config._sections.get("TASK", None):
        task_config_file_instance = Config._file_config._sections["TASK"][task_id]

    assert task_config_python_instance is not task_config_applied_instance
    assert task_config_python_instance is not task_config_instance_via_sequence
    assert task_config_file_instance is not task_config_applied_instance
    assert task_config_file_instance is not task_config_instance_via_sequence
    assert task_config_instance_via_sequence is task_config_applied_instance


def test_task_instance_when_configure_sequence_in_python():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    Config.configure_sequence("sequences1", [task1_config, task2_config])

    _check_tasks_instance("task1", "sequences1")
    _check_tasks_instance("task2", "sequences1")


def test_task_instance_when_configure_sequence_by_loading_toml():
    toml_config = _configure_sequence_in_toml()
    Config.load(toml_config.filename)

    _check_tasks_instance("task1", "sequences1")
    _check_tasks_instance("task2", "sequences1")


def test_task_instance_when_configure_sequence_by_overriding_toml():
    toml_config = _configure_sequence_in_toml()
    Config.override(toml_config.filename)

    _check_tasks_instance("task1", "sequences1")
    _check_tasks_instance("task2", "sequences1")


def test_sequence_config_creation():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    sequence_config = Config.configure_sequence("sequences1", [task1_config, task2_config])

    assert list(Config.sequences) == ["default", sequence_config.id]

    sequence2_config = Config.configure_sequence("sequences2", [task1_config, task2_config])
    assert list(Config.sequences) == ["default", sequence_config.id, sequence2_config.id]


def test_sequence_count():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    Config.configure_sequence("sequences1", [task1_config, task2_config])
    assert len(Config.sequences) == 2

    Config.configure_sequence("sequences2", [task1_config, task2_config])
    assert len(Config.sequences) == 3

    Config.configure_sequence("sequences3", [task1_config, task2_config])
    assert len(Config.sequences) == 4


def test_sequence_getitem():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    sequence_config_id = "sequences1"
    sequence = Config.configure_sequence(sequence_config_id, [task1_config, task2_config])

    assert Config.sequences[sequence_config_id].id == sequence.id
    assert Config.sequences[sequence_config_id]._tasks == sequence._tasks
    assert Config.sequences[sequence_config_id].properties == sequence.properties


def test_sequence_creation_no_duplication():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    Config.configure_sequence("sequences1", [task1_config, task2_config])

    assert len(Config.sequences) == 2

    Config.configure_sequence("sequences1", [task1_config, task2_config])
    assert len(Config.sequences) == 2


def test_sequence_config_with_env_variable_value():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    with mock.patch.dict(os.environ, {"FOO": "bar"}):
        Config.configure_sequence("sequence_name", [task1_config, task2_config], prop="ENV[FOO]")
        assert Config.sequences["sequence_name"].prop == "bar"
        assert Config.sequences["sequence_name"].properties["prop"] == "bar"
        assert Config.sequences["sequence_name"]._properties["prop"] == "ENV[FOO]"


def test_clean_config():
    task1_config = Config.configure_task("task1", print, [], [])
    task2_config = Config.configure_task("task2", print, [], [])
    sequence1_config = Config.configure_sequence("id1", [task1_config, task2_config])
    sequence2_config = Config.configure_sequence("id2", [task2_config, task1_config])

    assert Config.sequences["id1"] is sequence1_config
    assert Config.sequences["id2"] is sequence2_config

    sequence1_config._clean()
    sequence2_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.sequences["id1"] is sequence1_config
    assert Config.sequences["id2"] is sequence2_config

    assert sequence1_config.id == "id1"
    assert sequence2_config.id == "id2"
    assert sequence1_config.tasks == sequence2_config.tasks == []
    assert sequence1_config.properties == sequence2_config.properties == {}
