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

from datetime import datetime
from typing import Dict, List, Optional, Set, Union

from .._repository._abstract_converter import _AbstractConverter
from .._version._utils import _migrate_entity
from ..common import _utils
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..cycle.cycle import Cycle, CycleId
from ..data.data_node import DataNode, DataNodeId
from ..scenario._scenario_model import _ScenarioModel
from ..scenario.scenario import Scenario
from ..task.task import Task, TaskId


class _ScenarioConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, scenario: Scenario) -> _ScenarioModel:
        sequences: Dict[str, Dict[str, Union[List[TaskId], Dict, List]]] = {}
        for p_name, sequence_data in scenario._sequences.items():
            sequences[p_name] = {
                Scenario._SEQUENCE_TASKS_KEY: [
                    t.id if isinstance(t, Task) else t for t in sequence_data.get("tasks", [])
                ],
                Scenario._SEQUENCE_PROPERTIES_KEY: sequence_data.get("properties", {}),
                Scenario._SEQUENCE_SUBSCRIBERS_KEY: _utils._fcts_to_dict(sequence_data.get("subscribers", [])),
            }

        return _ScenarioModel(
            id=scenario.id,
            config_id=scenario.config_id,
            tasks=[task.id if isinstance(task, Task) else TaskId(str(task)) for task in list(scenario._tasks)],
            additional_data_nodes=[
                dn.id if isinstance(dn, DataNode) else DataNodeId(str(dn))
                for dn in list(scenario._additional_data_nodes)
            ],
            properties=scenario._properties.data,
            creation_date=scenario._creation_date.isoformat(),
            primary_scenario=scenario._primary_scenario,
            subscribers=_utils._fcts_to_dict(scenario._subscribers),
            tags=list(scenario._tags),
            version=scenario._version,
            cycle=scenario._cycle.id if scenario._cycle else None,
            sequences=sequences if sequences else None,
        )

    @classmethod
    def _model_to_entity(cls, model: _ScenarioModel) -> Scenario:
        tasks: Union[Set[TaskId], Set[Task], Set] = set()
        if model.tasks:
            tasks = set(model.tasks)
        if model.sequences:
            for sequence_name, sequence_data in model.sequences.items():
                if subscribers := sequence_data.get(Scenario._SEQUENCE_SUBSCRIBERS_KEY):
                    model.sequences[sequence_name][Scenario._SEQUENCE_SUBSCRIBERS_KEY] = [
                        _utils._Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                        for it in subscribers
                    ]

        scenario = Scenario(
            scenario_id=model.id,
            config_id=model.config_id,
            tasks=tasks,
            additional_data_nodes=set(model.additional_data_nodes),
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            is_primary=model.primary_scenario,
            tags=set(model.tags),
            cycle=cls.__to_cycle(model.cycle),
            subscribers=[
                _utils._Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                for it in model.subscribers
            ],
            version=model.version,
            sequences=model.sequences,
        )
        return _migrate_entity(scenario)

    @staticmethod
    def __to_cycle(cycle_id: Optional[CycleId] = None) -> Optional[Cycle]:
        return _CycleManagerFactory._build_manager()._get(cycle_id) if cycle_id else None
