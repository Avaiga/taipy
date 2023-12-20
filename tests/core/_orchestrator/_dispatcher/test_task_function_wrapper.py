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

import random
import string

from taipy.config import Config
from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.common.scope import Scope
from taipy.config.exceptions import ConfigurationUpdateBlocked
from taipy.core._orchestrator._dispatcher._task_function_wrapper import _TaskFunctionWrapper
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.data._data_manager import _DataManager
from taipy.core.task.task import Task


def _create_task(function, nb_outputs=1):
    output_dn_config_id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    dn_input_configs = [
        Config.configure_data_node("input1", "pickle", Scope.SCENARIO, default_data=21),
        Config.configure_data_node("input2", "pickle", Scope.SCENARIO, default_data=2),
    ]
    dn_output_configs = [
        Config.configure_data_node(f"{output_dn_config_id}_output{i}", "pickle", Scope.SCENARIO, default_data=0)
        for i in range(nb_outputs)
    ]
    input_dn = _DataManager._bulk_get_or_create(dn_input_configs).values()
    output_dn = _DataManager._bulk_get_or_create(dn_output_configs).values()
    return Task(
        output_dn_config_id,
        {},
        function=function,
        input=input_dn,
        output=output_dn,
    )


def multiply(nb1: float, nb2: float):
    return nb1 * nb2


def test_execute_task_that_return_multiple_outputs():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    with_tuple = _create_task(return_2tuple, 2)
    with_list = _create_task(return_list, 2)
    _TaskFunctionWrapper("job_id_tuple", with_tuple).execute()
    _TaskFunctionWrapper("job_id_list", with_list).execute()

    assert (
        with_tuple.output[f"{with_tuple.config_id}_output0"].read()
        == with_list.output[f"{with_list.config_id}_output0"].read()
        == 42
    )
    assert (
        with_tuple.output[f"{with_tuple.config_id}_output1"].read()
        == with_list.output[f"{with_list.config_id}_output1"].read()
        == 21
    )


def test_execute_task_that_returns_single_iterable_output():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    task_with_tuple = _create_task(return_2tuple, 1)
    task_with_list = _create_task(return_list, 1)
    _TaskFunctionWrapper("job_id_tuple", task_with_tuple).execute()
    _TaskFunctionWrapper("job_id_list", task_with_list).execute()

    assert task_with_tuple.output[f"{task_with_tuple.config_id}_output0"].read() == (42, 21)
    assert len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0
    assert task_with_list.output[f"{task_with_list.config_id}_output0"].read() == [42, 21]
    assert len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0


def test_data_node_not_written_due_to_wrong_result_nb():
    def fct_2_outputs():
        return lambda nb1, nb2: (multiply(nb1, nb2), multiply(nb1, nb2) / 2)

    task_expecting_3_outputs = _create_task(fct_2_outputs, 3)

    exceptions = _TaskFunctionWrapper("job_id", task_expecting_3_outputs).execute()

    assert len(exceptions) == 1
    assert isinstance(exceptions[0], Exception)


def test_cannot_exec_task_that_update_config():
    def update_config_fct(n, m):
        from taipy.config import Config

        Config.core.storage_folder = ".new_storage_folder/"
        return n * m

    task_updating_cfg = _create_task(update_config_fct)
    cfg_as_str = _TomlSerializer()._serialize(Config._applied_config)
    res = _TaskFunctionWrapper("job_id", task_updating_cfg).execute(config_as_string=cfg_as_str)

    assert len(res) == 1
    assert isinstance(res[0], ConfigurationUpdateBlocked)


def test_can_execute_task_with_a_modified_config():
    def assert_config_is_correct_after_serialization(n, m):
        from taipy.config import Config

        assert Config.core.storage_folder == ".my_data/"
        assert Config.core.custom_property == "custom_property"
        return n * m

    Config.configure_core(storage_folder=".my_data/", custom_property="custom_property")

    task_asserting_cfg_is_correct = _create_task(assert_config_is_correct_after_serialization)
    cfg_as_str = _TomlSerializer()._serialize(Config._applied_config)
    res = _TaskFunctionWrapper("job_id", task_asserting_cfg_is_correct).execute(config_as_string=cfg_as_str)

    assert len(res) == 0  # no exception raised so the asserts in the fct passed
