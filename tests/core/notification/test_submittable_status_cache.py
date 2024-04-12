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

from datetime import datetime

from taipy.config import Config, Frequency
from taipy.core.notification._submittable_status_cache import SubmittableStatusCache
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory


def test_get_reason_submittable_is_not_ready_to_submit():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    assert len(scenario_manager._get_all()) == 0

    dn_config_1 = Config.configure_pickle_data_node("dn_1", default_data=10)
    dn_config_2 = Config.configure_pickle_data_node("dn_2", default_data=15)
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2])
    scenario_config = Config.configure_scenario("sc", {task_config}, set(), Frequency.DAILY)
    scenario = scenario_manager._create(scenario_config)
    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2

    dn_2.edit_in_progress = True
    assert not scenario.is_ready_to_run()
    assert not scenario_manager._is_submittable(scenario)
    assert (
        SubmittableStatusCache.get_reason_submittable_is_not_ready_to_submit(scenario.id)
        == f"DataNode {dn_2.id} is being edited."
    )

    dn_1.last_edit_date = None
    assert not scenario.is_ready_to_run()
    assert not scenario_manager._is_submittable(scenario)
    assert (
        SubmittableStatusCache.get_reason_submittable_is_not_ready_to_submit(scenario.id)
        == f"DataNode {dn_2.id} is being edited; DataNode {dn_1.id} is not written."
    )

    dn_2.edit_in_progress = False
    assert not scenario.is_ready_to_run()
    assert not scenario_manager._is_submittable(scenario)
    assert (
        SubmittableStatusCache.get_reason_submittable_is_not_ready_to_submit(scenario.id)
        == f"DataNode {dn_1.id} is not written."
    )

    dn_1.last_edit_date = datetime.now()
    assert scenario.is_ready_to_run()
    assert scenario_manager._is_submittable(scenario)
    assert SubmittableStatusCache.get_reason_submittable_is_not_ready_to_submit(scenario.id) == ""
