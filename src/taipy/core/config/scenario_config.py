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

from collections import defaultdict
from copy import copy
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.config._config import _Config
from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.common._validate_id import _validate_id
from taipy.config.common.frequency import Frequency
from taipy.config.config import Config
from taipy.config.section import Section

from .pipeline_config import PipelineConfig
from .task_config import TaskConfig


class ScenarioConfig(Section):
    """
    Holds all the configuration fields needed to instantiate an actual `Scenario^` from the `ScenarioConfig`.

    Attributes:
        id (str): Identifier of the scenario config. It must be a valid Python variable name.
        pipeline_configs (Union[PipelineConfig, List[PipelineConfig]]): List of pipeline configs. The default value
            is [].
        **properties (dict[str, Any]): A dictionary of additional properties.
    """

    name = "SCENARIO"

    _PIPELINE_KEY = "pipelines"
    _FREQUENCY_KEY = "frequency"
    _COMPARATOR_KEY = "comparators"

    def __init__(
        self,
        id: str,
        pipelines: Union[PipelineConfig, List[PipelineConfig]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        if pipelines:
            self._pipelines = [pipelines] if isinstance(pipelines, PipelineConfig) else copy(pipelines)
        else:
            self._pipelines = []
        self.frequency = frequency
        self.comparators = defaultdict(list)
        if comparators:
            for k, v in comparators.items():
                if isinstance(v, list):
                    self.comparators[_validate_id(k)].extend(v)
                else:
                    self.comparators[_validate_id(k)].append(v)
        super().__init__(id, **properties)

    def __copy__(self):
        comp = None if self.comparators is None else self.comparators
        return ScenarioConfig(self.id, copy(self._pipelines), self.frequency, copy(comp), **copy(self._properties))

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @property
    def pipeline_configs(self) -> List[PipelineConfig]:
        return self._pipelines

    @property
    def pipelines(self) -> List[PipelineConfig]:
        return self._pipelines

    @classmethod
    def default_config(cls):
        return ScenarioConfig(cls._DEFAULT_KEY, [], None, dict())

    def _to_dict(self):
        return {
            self._COMPARATOR_KEY: self.comparators,
            self._PIPELINE_KEY: self._pipelines,
            self._FREQUENCY_KEY: self.frequency,
            **self._properties,
        }

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config]):  # type: ignore
        as_dict.pop(cls._ID_KEY, id)
        p_configs = config._sections[PipelineConfig.name]  # type: ignore
        pipelines = []
        if pipeline_ids := as_dict.pop(cls._PIPELINE_KEY, None):
            pipelines = [p_configs[p_id] for p_id in pipeline_ids if p_id in p_configs]
        frequency = as_dict.pop(cls._FREQUENCY_KEY, None)
        comparators = as_dict.pop(cls._COMPARATOR_KEY, dict())
        return ScenarioConfig(id=id, pipelines=pipelines, frequency=frequency, comparators=comparators, **as_dict)

    def _update(self, as_dict, default_section=None):
        self._pipelines = as_dict.pop(self._PIPELINE_KEY, self._pipelines)
        if self._pipelines is None and default_section:
            self._pipelines = default_section._pipelines
        self.frequency = as_dict.pop(self._FREQUENCY_KEY, self.frequency)
        if self.frequency is None and default_section:
            self.frequency = default_section.frequency
        self.comparators = as_dict.pop(self._COMPARATOR_KEY, self.comparators)
        if self.comparators is None and default_section:
            self.comparators = default_section.comparators
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    def add_comparator(self, dn_config_id: str, comparator: Callable):
        self.comparators[dn_config_id].append(comparator)

    def delete_comparator(self, dn_config_id: str):
        if dn_config_id in self.comparators:
            del self.comparators[dn_config_id]

    @staticmethod
    def _configure(
        id: str,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        """Configure a new scenario configuration.

        Parameters:
            id (str): The unique identifier of the new scenario configuration.
            pipeline_configs (List[PipelineConfig^]): The list of pipeline configurations used
                by this new scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to the
                relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `(taipy.)compare_scenarios()^` more more details.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `ScenarioConfig^`: The new scenario configuration.
        """
        section = ScenarioConfig(id, pipeline_configs, frequency=frequency, comparators=comparators, **properties)
        Config._register(section)
        return Config.sections[ScenarioConfig.name][id]

    @staticmethod
    def _configure_from_tasks(
        id: str,
        task_configs: List[TaskConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        pipeline_id: Optional[str] = None,
        **properties,
    ):
        """Configure a new scenario configuration made of a single new pipeline configuration.

        A new pipeline configuration is created as well. If _pipeline_id_ is not provided,
        the new pipeline configuration identifier is set to the scenario configuration identifier
        post-fixed by '_pipeline'.

        Parameters:
            id (str): The unique identifier of the scenario configuration.
            task_configs (List[TaskConfig^]): The list of task configurations used by the
                new pipeline configuration that is created.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to the
                relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `(taipy.)compare_scenarios()` more more details.
            pipeline_id (str): The identifier of the new pipeline configuration to be
                configured.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `ScenarioConfig^`: The new scenario configuration.
        """
        if not pipeline_id:
            pipeline_id = f"{id}_pipeline"
        pipeline_config = Config.configure_pipeline(pipeline_id, task_configs, **properties)
        section = ScenarioConfig(id, [pipeline_config], frequency=frequency, comparators=comparators, **properties)
        Config._register(section)
        return Config.sections[ScenarioConfig.name][id]

    @staticmethod
    def _configure_default(
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        """Configure the default values for scenario configurations.

        This function creates the _default scenario configuration_ object,
        where all scenario configuration objects will find their default
        values when needed.

        Parameters:
            pipeline_configs (List[PipelineConfig^]): The list of pipeline configurations used
                by this scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to
                the relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `taipy.compare_scenarios()^` more more details.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `ScenarioConfig^`: The default scenario configuration.
        """
        section = ScenarioConfig(
            _Config.DEFAULT_KEY, pipeline_configs, frequency=frequency, comparators=comparators, **properties
        )
        Config._register(section)
        return Config.sections[ScenarioConfig.name][_Config.DEFAULT_KEY]
