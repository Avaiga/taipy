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
from typing import Optional

from .._repository._v2._abstract_converter import _AbstractConverter
from .._version._utils import _migrate_entity
from ..common._utils import _fcts_to_dict, _load_fct, _Subscriber
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..cycle.cycle import Cycle, CycleId
from ..pipeline.pipeline import Pipeline
from ..scenario._scenario_model import _ScenarioModel
from ..scenario.scenario import Scenario


class _ScenarioConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, scenario: Scenario) -> _ScenarioModel:
        return _ScenarioModel(
            id=scenario.id,
            config_id=scenario.config_id,
            pipelines=[p.id if isinstance(p, Pipeline) else p for p in scenario._pipelines],
            properties=scenario._properties.data,
            creation_date=scenario._creation_date.isoformat(),
            primary_scenario=scenario._primary_scenario,
            subscribers=_fcts_to_dict(scenario._subscribers),
            tags=list(scenario._tags),
            version=scenario.version,
            cycle=scenario._cycle.id if scenario._cycle else None,
        )

    @classmethod
    def _model_to_entity(cls, model: _ScenarioModel) -> Scenario:
        scenario = Scenario(
            scenario_id=model.id,
            config_id=model.config_id,
            pipelines=model.pipelines,
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            is_primary=model.primary_scenario,
            tags=set(model.tags),
            cycle=cls.__to_cycle(model.cycle),
            subscribers=[
                _Subscriber(_load_fct(it["fct_module"], it["fct_name"]), it["fct_params"]) for it in model.subscribers
            ],
            version=model.version,
        )
        return _migrate_entity(scenario)

    @staticmethod
    def __to_cycle(cycle_id: Optional[CycleId] = None) -> Optional[Cycle]:
        return _CycleManagerFactory._build_manager()._get(cycle_id) if cycle_id else None
