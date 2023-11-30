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

from src.taipy.core._entity._entity_ids import _EntityIds


class TestEntityIds:
    def test_add_two_entity_ids(self):
        entity_ids_1 = _EntityIds()
        entity_ids_2 = _EntityIds()

        entity_ids_1_address = id(entity_ids_1)

        entity_ids_1.data_node_ids.update(["data_node_id_1", "data_node_id_2"])
        entity_ids_1.task_ids.update(["task_id_1", "task_id_2"])
        entity_ids_1.job_ids.update(["job_id_1", "job_id_2"])
        entity_ids_1.sequence_ids.update(["sequence_id_1", "sequence_id_2"])
        entity_ids_1.scenario_ids.update(["scenario_id_1", "scenario_id_2"])
        entity_ids_1.cycle_ids.update(["cycle_id_1", "cycle_id_2"])

        entity_ids_2.data_node_ids.update(["data_node_id_2", "data_node_id_3"])
        entity_ids_2.task_ids.update(["task_id_2", "task_id_3"])
        entity_ids_2.job_ids.update(["job_id_2", "job_id_3"])
        entity_ids_2.sequence_ids.update(["sequence_id_2", "sequence_id_3"])
        entity_ids_2.scenario_ids.update(["scenario_id_2", "scenario_id_3"])
        entity_ids_2.cycle_ids.update(["cycle_id_2", "cycle_id_3"])

        entity_ids_1 += entity_ids_2

        # += operator should not change the address of entity_ids_1
        assert id(entity_ids_1) == entity_ids_1_address

        assert entity_ids_1.data_node_ids == {"data_node_id_1", "data_node_id_2", "data_node_id_3"}
        assert entity_ids_1.task_ids == {"task_id_1", "task_id_2", "task_id_3"}
        assert entity_ids_1.job_ids == {"job_id_1", "job_id_2", "job_id_3"}
        assert entity_ids_1.sequence_ids == {"sequence_id_1", "sequence_id_2", "sequence_id_3"}
        assert entity_ids_1.scenario_ids == {"scenario_id_1", "scenario_id_2", "scenario_id_3"}
        assert entity_ids_1.cycle_ids == {"cycle_id_1", "cycle_id_2", "cycle_id_3"}
