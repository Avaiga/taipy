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

from .data_node_config import DataNodeConfig
from .pipeline_config import PipelineConfig
from .task_config import TaskConfig


class ScenarioConfig(Section):
    """
    Configuration fields needed to instantiate an actual `Scenario^`.

    Attributes:
        id (str): Identifier of the scenario config. It must be a valid Python variable name.
        tasks_and_data_nodes (Union[TaskConfig, DataNodeConfig, List[Union[TaskConfig, DataNodeConfig]]]): List of task and data node configs.<br/>
            The default value is [].
        **properties (dict[str, any]): A dictionary of additional properties.
    """

    name = "SCENARIO"

    _PIPELINE_KEY = "pipelines"
    _TASKS_AND_DATANODES_KEY = "tasks_and_data_nodes"
    _FREQUENCY_KEY = "frequency"
    _COMPARATOR_KEY = "comparators"

    def __init__(
        self,
        id: str,
        tasks_and_data_nodes: Union[TaskConfig, DataNodeConfig, List[Union[TaskConfig, DataNodeConfig]]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        if tasks_and_data_nodes:
            self._tasks_and_data_nodes = (
                [tasks_and_data_nodes]
                if isinstance(tasks_and_data_nodes, DataNodeConfig) or isinstance(tasks_and_data_nodes, TaskConfig)
                else copy(tasks_and_data_nodes)
            )
        else:
            self._tasks_and_data_nodes = []
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
        return ScenarioConfig(
            self.id, copy(self._tasks_and_data_nodes), self.frequency, copy(comp), **copy(self._properties)
        )

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @property
    def task_and_data_node_configs(self) -> List[Union[TaskConfig, DataNodeConfig]]:
        # TODO: return also dn that already defined in task?
        return self._tasks_and_data_nodes

    @property
    def tasks_and_data_nodes(self) -> List[Union[TaskConfig, DataNodeConfig]]:
        # TODO: return also dn that already defined in task?
        return self._tasks_and_data_nodes

    @classmethod
    def default_config(cls):
        return ScenarioConfig(cls._DEFAULT_KEY, [], None, dict())

    def _clean(self):
        self._tasks_and_data_nodes = []
        self.frequency = None
        self.comparators = dict()
        self._properties.clear()

    def _to_dict(self):
        return {
            self._COMPARATOR_KEY: self.comparators,
            self._TASKS_AND_DATANODES_KEY: self._tasks_and_data_nodes,
            self._FREQUENCY_KEY: self.frequency,
            **self._properties,
        }

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config]):  # type: ignore
        as_dict.pop(cls._ID_KEY, id)
        tasks_and_data_nodes = []
        if task_and_data_node_ids := as_dict.pop(cls._TASKS_AND_DATANODES_KEY, None):
            task_configs = config._sections[TaskConfig.name]  # type: ignore
            data_node_configs = config._sections[DataNodeConfig.name]  # type: ignore
            for t_or_dn_ids in task_and_data_node_ids:
                if task_config := task_configs.get(t_or_dn_ids, None):
                    tasks_and_data_nodes.append(task_config)
                if data_node_config := data_node_configs.get(t_or_dn_ids, None):
                    tasks_and_data_nodes.append(data_node_config)
        else:
            # Check if pipeline configs exist, if yes, migrate by getting all task configs and ignore pipeline configs
            if pipeline_ids := as_dict.pop(cls._PIPELINE_KEY, None):
                p_configs = config._sections[PipelineConfig.name]  # type: ignore
                for p_id in pipeline_ids:
                    if pipeline_config := p_configs.get(p_id, None):
                        tasks_and_data_nodes.extend(pipeline_config.tasks)
        frequency = as_dict.pop(cls._FREQUENCY_KEY, None)
        comparators = as_dict.pop(cls._COMPARATOR_KEY, dict())
        return ScenarioConfig(
            id=id, tasks_and_data_nodes=tasks_and_data_nodes, frequency=frequency, comparators=comparators, **as_dict
        )

    def _update(self, as_dict, default_section=None):
        self._tasks_and_data_nodes = as_dict.pop(self._TASKS_AND_DATANODES_KEY, self._tasks_and_data_nodes)
        if self._tasks_and_data_nodes is None and default_section:
            self._tasks_and_data_nodes = default_section._tasks_and_data_nodes
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
        task_and_data_node_configs: List[Union[TaskConfig, DataNodeConfig]],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ) -> "ScenarioConfig":
        """Configure a new scenario configuration.

        Parameters:
            id (str): The unique identifier of the new scenario configuration.
            task_and_data_node_configs (List[Union[TaskConfig^, DataNodeConfig^]]): The list of task and data node configurations used
                by this new scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.<br/>
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
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new scenario configuration.
        """
        section = ScenarioConfig(
            id, task_and_data_node_configs, frequency=frequency, comparators=comparators, **properties
        )
        Config._register(section)
        return Config.sections[ScenarioConfig.name][id]

    @staticmethod
    def _configure_default(
        task_and_data_node_configs: List[Union[TaskConfig, DataNodeConfig]],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ) -> "ScenarioConfig":
        """Configure the default values for scenario configurations.

        This function creates the *default scenario configuration* object,
        where all scenario configuration objects will find their default
        values when needed.

        Parameters:
            task_and_data_node_configs (List[Union[TaskConfig^, DataNodeConfig^]]): The list of task and data node configurations used
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
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new default scenario configuration.
        """
        section = ScenarioConfig(
            _Config.DEFAULT_KEY, task_and_data_node_configs, frequency=frequency, comparators=comparators, **properties
        )
        Config._register(section)
        return Config.sections[ScenarioConfig.name][_Config.DEFAULT_KEY]
