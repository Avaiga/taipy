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

import pytest

from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.sequence._sequence_manager import _SequenceManager
from src.taipy.core.sequence.sequence_id import SequenceId
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from src.taipy.core.task.task_id import TaskId
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from tests.core.conftest import init_managers


def test_set_and_get_sequence(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()
    _OrchestratorFactory._build_dispatcher()

    input_dn = InMemoryDataNode("foo", Scope.SCENARIO)
    output_dn = InMemoryDataNode("foo", Scope.SCENARIO)
    task = Task("task", {}, print, [input_dn], [output_dn], TaskId("task_id"))

    scenario = Scenario("scenario", {task}, {}, set())
    _ScenarioManager._set(scenario)

    sequence_name_1 = "p1"
    sequence_id_1 = SequenceId(f"SEQUENCE_{sequence_name_1}_{scenario.id}")
    sequence_name_2 = "p2"
    sequence_id_2 = SequenceId(f"SEQUENCE_{sequence_name_2}_{scenario.id}")

    # No existing Sequence
    assert _SequenceManager._get(sequence_id_1) is None
    assert _SequenceManager._get(sequence_id_2) is None

    scenario.add_sequences({sequence_name_1: []})
    sequence_1 = scenario.sequences[sequence_name_1]

    # Save one sequence. We expect to have only one sequence stored
    _SequenceManager._set(sequence_1)
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 0
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 0
    assert _SequenceManager._get(sequence_id_2) is None

    # Save a second sequence. Now, we expect to have a total of two sequences stored
    _TaskManager._set(task)
    scenario.add_sequences({sequence_name_2: [task]})
    sequence_2 = scenario.sequences[sequence_name_2]
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 0
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 0
    assert _SequenceManager._get(sequence_id_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_id_2).tasks) == 1
    assert _SequenceManager._get(sequence_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_2).tasks) == 1

    # We save the first sequence again. We expect nothing to change
    scenario.add_sequences({sequence_name_1: {}})
    sequence_1 = scenario.sequences[sequence_name_1]
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 0
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 0
    assert _SequenceManager._get(sequence_id_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_id_2).tasks) == 1
    assert _SequenceManager._get(sequence_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_2).tasks) == 1

    # We save a third sequence with same id as the first one.
    # We expect the first sequence to be updated
    scenario.add_sequences({sequence_name_1: [task]})
    sequence_3 = scenario.sequences[sequence_name_1]
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert _SequenceManager._get(sequence_id_1).id == sequence_3.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 1
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 1
    assert _SequenceManager._get(sequence_id_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_id_2).tasks) == 1
    assert _SequenceManager._get(sequence_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_2).tasks) == 1
    assert _TaskManager._get(task.id).id == task.id


def test_get_all_on_multiple_versions_environment(init_sql_repo):
    init_managers()

    # Create 5 sequences from Scenario with 2 versions each
    for version in range(1, 3):
        for i in range(5):
            _ScenarioManager._set(
                Scenario(
                    f"config_id_{i+version}",
                    [],
                    {},
                    [],
                    f"SCENARIO_id_{i}_v{version}",
                    version=f"{version}.0",
                    sequences={"sequence": {}},
                )
            )

    _VersionManager._set_experiment_version("1.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "1.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 1
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 0
    )

    _VersionManager._set_experiment_version("2.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 0
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v2"}])) == 1
    )

    _VersionManager._set_development_version("1.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "1.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 1
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "1.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v2"}])) == 0
    )

    _VersionManager._set_development_version("2.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 0
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v2"}])) == 1
    )


def mult_by_two(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_get_or_create_data(init_sql_repo):
    # only create intermediate data node once
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.SCENARIO, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    # dn_1 ---> mult_by_two ---> dn_2 ---> mult_by_3 ---> dn_6
    scenario_config = Config.configure_scenario("scenario", [task_config_mult_by_two, task_config_mult_by_3])

    _OrchestratorFactory._build_dispatcher()

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0

    scenario = _ScenarioManager._create(scenario_config)
    scenario.add_sequences({"by_6": list(scenario.tasks.values())})
    sequence = scenario.sequences["by_6"]

    assert sequence.name == "by_6"

    assert len(_DataManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 2
    assert len(sequence._get_sorted_tasks()) == 2
    assert sequence.foo.read() == 1
    assert sequence.bar.read() == 0
    assert sequence.baz.read() == 0
    assert sequence._get_sorted_tasks()[0][0].config_id == task_config_mult_by_two.id
    assert sequence._get_sorted_tasks()[1][0].config_id == task_config_mult_by_3.id

    _SequenceManager._submit(sequence.id)
    assert sequence.foo.read() == 1
    assert sequence.bar.read() == 2
    assert sequence.baz.read() == 6

    sequence.foo.write("new data value")
    assert sequence.foo.read() == "new data value"
    assert sequence.bar.read() == 2
    assert sequence.baz.read() == 6

    sequence.bar.write(7)
    assert sequence.foo.read() == "new data value"
    assert sequence.bar.read() == 7
    assert sequence.baz.read() == 6

    with pytest.raises(AttributeError):
        sequence.WRONG.write(7)


def test_hard_delete_one_single_sequence_with_scenario_data_nodes(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create([task_config])
    scenario = Scenario("scenario", set(tasks), {}, sequences={"sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["sequence"]
    sequence.submit()

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _SequenceManager._hard_delete(sequence.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_one_single_sequence_with_cycle_data_nodes(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create([task_config])
    scenario = Scenario("scenario", tasks, {}, sequences={"sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["sequence"]
    sequence.submit()

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _SequenceManager._hard_delete(sequence.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_shared_entities(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_1 = Config.configure_task("task_1", print, input_dn, intermediate_dn)
    task_2 = Config.configure_task("task_2", print, intermediate_dn, output_dn)

    _OrchestratorFactory._build_dispatcher()

    tasks_scenario_1 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_1")
    tasks_scenario_2 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_2")

    scenario_1 = Scenario("scenario_1", tasks_scenario_1, {}, sequences={"sequence": {"tasks": tasks_scenario_1}})
    scenario_2 = Scenario("scenario_2", tasks_scenario_2, {}, sequences={"sequence": {"tasks": tasks_scenario_2}})
    _ScenarioManager._set(scenario_1)
    _ScenarioManager._set(scenario_2)
    sequence_1 = scenario_1.sequences["sequence"]
    sequence_2 = scenario_2.sequences["sequence"]

    _SequenceManager._submit(sequence_1.id)
    _SequenceManager._submit(sequence_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
    _SequenceManager._hard_delete(sequence_1.id)
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
