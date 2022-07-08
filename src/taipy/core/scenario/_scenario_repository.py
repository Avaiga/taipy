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

import pathlib
from datetime import datetime
from typing import List, Optional

from taipy.config.config import Config

from .._repository import _RepositoryFactory
from ..common import _utils
from ..common._utils import Subscriber
from ..common.alias import CycleId, PipelineId
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..cycle.cycle import Cycle
from ..pipeline.pipeline import Pipeline
from ._scenario_model import _ScenarioModel
from .scenario import Scenario


class _ScenarioRepository(_RepositoryFactory.build_repository()[_ScenarioModel, Scenario]):  # type: ignore
    def __init__(self):
        kwargs = {
            "model": _ScenarioModel,
            "dir_name": "scenarios",
        }  # TODO: Change kwargs base on repository type when new ones are implemented

        super().__init__(**kwargs)

    def _to_model(self, scenario: Scenario):
        return _ScenarioModel(
            id=scenario.id,
            config_id=scenario.config_id,
            pipelines=self.__to_pipeline_ids(scenario._pipelines),
            properties=scenario._properties.data,
            creation_date=scenario._creation_date.isoformat(),
            primary_scenario=scenario._primary_scenario,
            subscribers=_utils._fcts_to_dict(scenario._subscribers),
            tags=list(scenario._tags),
            cycle=self.__to_cycle_id(scenario._cycle),
        )

    def _from_model(self, model: _ScenarioModel) -> Scenario:
        scenario = Scenario(
            scenario_id=model.id,
            config_id=model.config_id,
            pipelines=model.pipelines,  # type: ignore
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            is_primary=model.primary_scenario,
            tags=set(model.tags),
            cycle=self.__to_cycle(model.cycle),
            subscribers=[
                Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                for it in model.subscribers
            ],
        )
        return scenario

    @staticmethod
    def __to_pipeline_ids(pipelines) -> List[PipelineId]:
        return [p.id if isinstance(p, Pipeline) else p for p in pipelines]

    @staticmethod
    def __to_cycle(cycle_id: CycleId = None) -> Optional[Cycle]:
        return _CycleManagerFactory._build_manager()._get(cycle_id) if cycle_id else None

    @staticmethod
    def __to_cycle_id(cycle: Cycle = None) -> Optional[CycleId]:
        return cycle.id if cycle else None
