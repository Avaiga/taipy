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
from .task_config import TaskConfig


class ScenarioConfig(Section):
    """
    Configuration fields needed to instantiate an actual `Scenario^`.

    Attributes:
        id (str): Identifier of the scenario config. It must be a valid Python variable name.
        tasks (Optional[Union[TaskConfig, List[TaskConfig]]]): List of task configs.<br/>
            The default value is None.
        additional_data_nodes (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): <br/>
            List of additional data node configs. The default value is None.
        frequency (Optional[Frequency]): The frequency of the scenario's cycle. The default value is None.
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]]: Dictionary of the data node <br/>
            config id as key and a list of Callable used to compare the data nodes as value.
        sequences (Optional[Dict[str, List[TaskConfig]]]): Dictionary of sequence descriptions.
            The default value is None.
        **properties (dict[str, any]): A dictionary of additional properties.
    """

    name = "SCENARIO"

    _SEQUENCES_KEY = "sequences"
    _TASKS_KEY = "tasks"
    _ADDITIONAL_DATA_NODES_KEY = "additional_data_nodes"
    _FREQUENCY_KEY = "frequency"
    _SEQUENCES_KEY = "sequences"
    _COMPARATOR_KEY = "comparators"

    def __init__(
        self,
        id: str,
        tasks: Optional[Union[TaskConfig, List[TaskConfig]]] = None,
        additional_data_nodes: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        sequences: Optional[Dict[str, List[TaskConfig]]] = None,
        **properties,
    ):

        if tasks:
            self._tasks = list(tasks) if isinstance(tasks, TaskConfig) else copy(tasks)
        else:
            self._tasks = []

        if additional_data_nodes:
            self._additional_data_nodes = (
                list(additional_data_nodes)
                if isinstance(additional_data_nodes, DataNodeConfig)
                else copy(additional_data_nodes)
            )
        else:
            self._additional_data_nodes = []

        self.sequences = sequences if sequences else {}
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
        scenario_config = ScenarioConfig(
            self.id,
            copy(self._tasks),
            copy(self._additional_data_nodes),
            self.frequency,
            copy(comp),
            copy(self.sequences),
            **copy(self._properties),
        )
        return scenario_config

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @property
    def task_configs(self) -> List[TaskConfig]:
        return self._tasks

    @property
    def tasks(self) -> List[TaskConfig]:
        return self._tasks

    @property
    def additional_data_node_configs(self) -> List[DataNodeConfig]:
        return self._additional_data_nodes

    @property
    def additional_data_nodes(self) -> List[DataNodeConfig]:
        return self._additional_data_nodes

    @property
    def data_node_configs(self) -> List[DataNodeConfig]:
        return self.__get_all_unique_data_nodes()

    @property
    def data_nodes(self) -> List[DataNodeConfig]:
        return self.__get_all_unique_data_nodes()

    def __get_all_unique_data_nodes(self) -> List[DataNodeConfig]:
        data_node_configs = set(self._additional_data_nodes)
        for task in self._tasks:
            data_node_configs.update(task.inputs)
            data_node_configs.update(task.outputs)

        return list(data_node_configs)

    @classmethod
    def default_config(cls):
        return ScenarioConfig(cls._DEFAULT_KEY, list(), list(), None, dict())

    def _clean(self):
        self._tasks = list()
        self._additional_data_nodes = list()
        self.frequency = None
        self.comparators = dict()
        self.sequences = dict()
        self._properties = dict()

    def _to_dict(self) -> Dict[str, Any]:
        return {
            self._COMPARATOR_KEY: self.comparators,
            self._TASKS_KEY: self._tasks,
            self._ADDITIONAL_DATA_NODES_KEY: self._additional_data_nodes,
            self._FREQUENCY_KEY: self.frequency,
            self._SEQUENCES_KEY: self.sequences,
            **self._properties,
        }

    @classmethod
    def _from_dict(
        cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config] = None
    ) -> "ScenarioConfig":  # type: ignore
        as_dict.pop(cls._ID_KEY, id)

        tasks = cls.__get_task_configs(as_dict.pop(cls._TASKS_KEY, list()), config)

        additional_data_node_ids = as_dict.pop(cls._ADDITIONAL_DATA_NODES_KEY, list())
        additional_data_nodes = cls.__get_additional_data_node_configs(additional_data_node_ids, config)

        frequency = as_dict.pop(cls._FREQUENCY_KEY, None)
        comparators = as_dict.pop(cls._COMPARATOR_KEY, dict())
        sequences = as_dict.pop(cls._SEQUENCES_KEY, {})

        for sequence_name, sequence_tasks in sequences.items():
            sequences[sequence_name] = cls.__get_task_configs(sequence_tasks, config)

        scenario_config = ScenarioConfig(
            id=id,
            tasks=tasks,
            additional_data_nodes=additional_data_nodes,
            frequency=frequency,
            comparators=comparators,
            sequences=sequences,
            **as_dict,
        )

        return scenario_config

    @staticmethod
    def __get_task_configs(task_config_ids: List[str], config: Optional[_Config]):
        task_configs = set()
        if config:
            if task_config_section := config._sections.get(TaskConfig.name):
                for task_config_id in task_config_ids:
                    if task_config := task_config_section.get(task_config_id, None):
                        task_configs.add(task_config)
        return list(task_configs)

    @staticmethod
    def __get_additional_data_node_configs(additional_data_node_ids: List[str], config: Optional[_Config]):
        additional_data_node_configs = set()
        if config:
            if data_node_config_section := config._sections.get(DataNodeConfig.name):
                for additional_data_node_id in additional_data_node_ids:
                    if additional_data_node_config := data_node_config_section.get(additional_data_node_id):
                        additional_data_node_configs.add(additional_data_node_config)
        return list(additional_data_node_configs)

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        self._tasks = as_dict.pop(self._TASKS_KEY, self._tasks)
        if self._tasks is None and default_section:
            self._tasks = default_section._tasks

        self._additional_data_nodes = as_dict.pop(self._ADDITIONAL_DATA_NODES_KEY, self._additional_data_nodes)
        if self._additional_data_nodes is None and default_section:
            self._additional_data_nodes = default_section._additional_data_nodes

        self.frequency = as_dict.pop(self._FREQUENCY_KEY, self.frequency)
        if self.frequency is None and default_section:
            self.frequency = default_section.frequency

        self.comparators = as_dict.pop(self._COMPARATOR_KEY, self.comparators)
        if self.comparators is None and default_section:
            self.comparators = default_section.comparators

        self.sequences = as_dict.pop(self._SEQUENCES_KEY, self.sequences)
        if self.sequences is None and default_section:
            self.sequences = default_section.sequences

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
        task_configs: Optional[List[TaskConfig]] = None,
        additional_data_node_configs: Optional[List[DataNodeConfig]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        sequences: Optional[Dict[str, List[TaskConfig]]] = None,
        **properties,
    ) -> "ScenarioConfig":
        """Configure a new scenario configuration.

        Parameters:
            id (str): The unique identifier of the new scenario configuration.
            task_configs (Optional[List[TaskConfig^]]): The list of task configurations used by this
                scenario configuration. The default value is None.
            additional_data_node_configs (Optional[List[DataNodeConfig^]]): The list of additional data nodes
                related to this scenario configuration. The default value is None.
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
            sequences (Optional[Dict[str, List[TaskConfig]]]): Dictionary of sequence descriptions.
                The default value is None.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new scenario configuration.
        """
        section = ScenarioConfig(
            id,
            task_configs,
            additional_data_node_configs,
            frequency=frequency,
            comparators=comparators,
            sequences=sequences,
            **properties,
        )
        Config._register(section)
        return Config.sections[ScenarioConfig.name][id]

    @staticmethod
    def _set_default_configuration(
        task_configs: Optional[List[TaskConfig]] = None,
        additional_data_node_configs: List[DataNodeConfig] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        sequences: Optional[Dict[str, List[TaskConfig]]] = None,
        **properties,
    ) -> "ScenarioConfig":
        """Set the default values for scenario configurations.

        This function creates the *default scenario configuration* object,
        where all scenario configuration objects will find their default
        values when needed.

        Parameters:
            task_configs (Optional[List[TaskConfig^]]): The list of task configurations used by this
                scenario configuration.
            additional_data_node_configs (Optional[List[DataNodeConfig^]]): The list of additional data nodes
                related to this scenario configuration.
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
            sequences (Optional[Dict[str, List[TaskConfig]]]): Dictionary of sequences. The default value is None.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new default scenario configuration.
        """
        section = ScenarioConfig(
            _Config.DEFAULT_KEY,
            task_configs,
            additional_data_node_configs,
            frequency=frequency,
            comparators=comparators,
            sequences=sequences,
            **properties,
        )
        Config._register(section)
        return Config.sections[ScenarioConfig.name][_Config.DEFAULT_KEY]

    def add_sequences(self, sequences: Dict[str, List[TaskConfig]]):
        self.sequences.update(sequences)

    def remove_sequences(self, sequence_names: Union[str, List[str]]):
        if isinstance(sequence_names, List):
            for sequence_name in sequence_names:
                self.sequences.pop(sequence_name)
        else:
            self.sequences.pop(sequence_names)
