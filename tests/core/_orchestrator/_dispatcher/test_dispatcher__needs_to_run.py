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

from datetime import datetime, timedelta

import freezegun

from taipy.config import Config
from taipy.core._orchestrator._dispatcher import _JobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.task._task_manager import _TaskManager


def nothing(*args):
    pass


def _create_task_from_config(task_cfg):
    return _TaskManager()._bulk_get_or_create([task_cfg])[0]


def test_need_to_run_no_output():
    hello_cfg = Config.configure_data_node("hello", default_data="Hello ")
    world_cfg = Config.configure_data_node("world", default_data="world !")
    task_cfg = Config.configure_task("name", input=[hello_cfg, world_cfg], function=nothing, output=[])
    task = _create_task_from_config(task_cfg)
    assert _JobDispatcher(_OrchestratorFactory._build_orchestrator())._needs_to_run(task)


def test_need_to_run_task_not_skippable():
    hello_cfg = Config.configure_data_node("hello", default_data="Hello ")
    world_cfg = Config.configure_data_node("world", default_data="world !")
    hello_world_cfg = Config.configure_data_node("hello_world")
    task_cfg = Config.configure_task(
        "name", input=[hello_cfg, world_cfg], function=nothing, output=[hello_world_cfg], skippable=False
    )
    task = _create_task_from_config(task_cfg)

    assert _JobDispatcher(_OrchestratorFactory._build_orchestrator())._needs_to_run(task)


def test_need_to_run_skippable_task_no_input():
    hello_world_cfg = Config.configure_data_node("hello_world")
    task_cfg = Config.configure_task("name", input=[], function=nothing, output=[hello_world_cfg], skippable=True)
    task = _create_task_from_config(task_cfg)
    dispatcher = _JobDispatcher(_OrchestratorFactory._build_orchestrator())
    assert dispatcher._needs_to_run(task)  # output data is not written
    task.output["hello_world"].write("Hello world !")
    assert not dispatcher._needs_to_run(task)  # output data is written


def test_need_to_run_skippable_task_no_validity_period_on_output():
    hello_cfg = Config.configure_data_node("hello", default_data="Hello ")
    output_cfg = Config.configure_data_node("output")
    task_cfg = Config.configure_task(
        "name", input=[hello_cfg], function=nothing, output=[output_cfg], skippable=True
    )
    task = _create_task_from_config(task_cfg)
    dispatcher = _JobDispatcher(_OrchestratorFactory._build_orchestrator())
    assert dispatcher._needs_to_run(task)  # output data is not written
    task.output["output"].write("Hello world !")
    assert not dispatcher._needs_to_run(task)  # output data is written


def test_need_to_run_skippable_task_with_validity_period_on_output():
    hello_cfg = Config.configure_data_node("hello", default_data="Hello ")
    hello_world_cfg = Config.configure_data_node("output", validity_period=timedelta(days=1))
    task_cfg = Config.configure_task("name", nothing, [hello_cfg], [hello_world_cfg], skippable=True)
    task = _create_task_from_config(task_cfg)
    dispatcher = _JobDispatcher(_OrchestratorFactory._build_orchestrator())

    assert dispatcher._needs_to_run(task)  # output data is not edited

    output_edit_time = datetime.now() # edit time
    with freezegun.freeze_time(output_edit_time):
        task.output["output"].write("Hello world !")  # output data is edited

    with freezegun.freeze_time(output_edit_time + timedelta(minutes=30)):  # 30 min after edit time
        assert not dispatcher._needs_to_run(task)  # output data is written and validity period not expired

    with freezegun.freeze_time(output_edit_time + timedelta(days=1, seconds=1)): # 1 day and 1 second after edit time
        assert dispatcher._needs_to_run(task)  # output data is written but validity period expired

def test_need_to_run_skippable_task_but_input_edited_after_output():
    hello_cfg = Config.configure_data_node("input", default_data="Hello ")
    hello_world_cfg = Config.configure_data_node("output")
    task_cfg = Config.configure_task("name", nothing, [hello_cfg], [hello_world_cfg], skippable=True)
    task = _create_task_from_config(task_cfg)
    dispatcher = _JobDispatcher(_OrchestratorFactory._build_orchestrator())
    output_edit_time = datetime.now()
    with freezegun.freeze_time(output_edit_time):
        task.data_nodes["output"].write("Hello world !")  # output data is edited at output_edit_time

    with freezegun.freeze_time(output_edit_time + timedelta(minutes=30)):  # 30 min after output_edit_time
        task.data_nodes["input"].write("Yellow !")
        assert dispatcher._needs_to_run(task)  # output data is written but validity period expired
