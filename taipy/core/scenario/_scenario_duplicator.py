# Copyright 2021-2025 Avaiga Private Limited
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
from typing import Dict, Optional, Set, Union

from taipy.common.config import Config

from ..common._listattributes import _ListAttributes
from ..common.scope import Scope
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..data._data_duplicator import _DataDuplicator
from ..data._data_manager_factory import _DataManagerFactory
from ..data.data_node import DataNode
from ..notification import EventOperation, Notifier, _make_event
from ..sequence.sequence import Sequence
from ..task._task_manager_factory import _TaskManagerFactory
from ..task.task import Task
from .scenario import Scenario


class _ScenarioDuplicator:
    """A service to duplicate a scenario and related entities."""

    def __init__(self, scenario: Scenario, data_to_duplicate: Union[bool, Set[str]]=True):
        self.scenario: Scenario = scenario
        if data_to_duplicate is True:
            self.data_to_duplicate: Set[str] = set(self.scenario.data_nodes.keys())
        elif isinstance(data_to_duplicate, set):
            self.data_to_duplicate = data_to_duplicate
        else:
            self.data_to_duplicate = set()

        self.new_scenario: Scenario = None  # type: ignore
        self.new_cycle_id: Optional[str] = None
        self.new_tasks: Dict[str, Task] = {}
        self.new_data_nodes: Dict[str, DataNode] = {}

        from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
        self.__scenario_manager = _ScenarioManagerFactory._build_manager()
        self.__cycle_manager = _CycleManagerFactory._build_manager()
        self.__task_manager = _TaskManagerFactory._build_manager()
        self.__data_manager = _DataManagerFactory._build_manager()

    def duplicate(self, new_creation_date: Optional[datetime]=None, new_name: Optional[str]=None) -> Scenario:
        """Create a duplicated scenario with its related entities

        Create a scenario with the same configuration as the original scenario, but with
        a new creation date and name. Creation events are published for the new scenario,
        tasks, and data nodes. The data nodes are duplicated if the `data_to_duplicate`
        is set to True or a set of data node configuration ids. The new scenario is returned.

        Arguments:
            new_creation_date (Optional[datetime]): The creation date of the new scenario.
                If not provided, the current date and time is used.
            new_name (Optional[str]): The name of the new scenario. If not provided, the
                name of the original scenario is used.

        Returns:
            The newly created scenario.
        """
        self.new_scenario = self.__init_new_scenario(new_creation_date or datetime.now(), new_name)
        for dn in self.scenario.additional_data_nodes.values():
            self.new_scenario._additional_data_nodes.add(self._duplicate_datanode(dn).id)  # type: ignore
        for task in self.scenario.tasks.values():
            self.new_scenario._tasks.add(self._duplicate_task(task).id)  # type: ignore
        self._duplicate_sequences()
        self.__scenario_manager._set(self.new_scenario)
        Notifier.publish(_make_event(self.new_scenario, EventOperation.CREATION))
        return self.new_scenario

    def _duplicate_task(self, task: Task) -> Task:
        if task.scope == Scope.GLOBAL:
            # Task and children data nodes already exist. No need to duplicate.
            self.new_tasks[task.config_id] = task
            task._parent_ids.update([self.new_scenario.id])
            self.__task_manager._repository._save(task) # Through the repository so we don't set data nodes
            Notifier.publish(_make_event(task, EventOperation.UPDATE, "parent_ids", task._parent_ids))
            return task
        if task.scope == Scope.CYCLE and self.scenario.cycle.id == self.new_cycle_id:
            # Task and children data nodes already exist. No need to duplicate.
            self.new_tasks[task.config_id] = task
            task._parent_ids.update([self.new_scenario.id])
            self.__task_manager._repository._save(task) # Through the repository so we don't set data nodes
            Notifier.publish(_make_event(task, EventOperation.UPDATE, "parent_ids", task._parent_ids))
            return task
        if task.scope == Scope.CYCLE:
            existing_tasks = self.__task_manager._repository._get_by_configs_and_owner_ids(  # type: ignore
                [(task.config_id, self.new_cycle_id)],
                self.__task_manager._build_filters_with_version(None))
            if existing_tasks:
                # Task and children data nodes already exist. No need to duplicate.
                existing_t = existing_tasks[(task.config_id,self.new_cycle_id)]
                self.new_tasks[task.config_id] = existing_t
                existing_t._parent_ids.update([self.new_scenario.id])
                self.__task_manager._repository._save(existing_t)  # Don't set data nodes
                Notifier.publish(_make_event(existing_t, EventOperation.UPDATE, "parent_ids", existing_t._parent_ids))
                return existing_t

        new_task = self.__init_new_task(task)
        for input in task.input.values():
            new_task._input[input.config_id] = self._duplicate_datanode(input, new_task)
        for output in task.output.values():
            new_task._output[output.config_id] = self._duplicate_datanode(output, new_task)
        self.new_tasks[task.config_id] = new_task

        self.__task_manager._set(new_task)
        Notifier.publish(_make_event(new_task, EventOperation.CREATION))
        return new_task

    def _duplicate_datanode(self, dn: DataNode, task: Optional[Task]=None) -> DataNode:
        if dn.config_id in self.new_data_nodes:
            # Data node already created from another task. No need to duplicate.
            new_dn = self.new_data_nodes[dn.config_id]
            new_dn._parent_ids.update([task.id]) if task else new_dn._parent_ids.update([self.new_scenario.id])
            self.__data_manager._set(new_dn)
            Notifier.publish(_make_event(new_dn, EventOperation.UPDATE, "parent_ids", new_dn._parent_ids))
            return new_dn
        if dn.scope == Scope.GLOBAL:
            # Data node already exists. No need to duplicate.
            dn._parent_ids.update([task.id]) if task else dn._parent_ids.update([self.new_scenario.id])
            self.__data_manager._set(dn)
            Notifier.publish(_make_event(dn, EventOperation.UPDATE, "parent_ids", dn._parent_ids))
            return dn
        if dn.scope == Scope.CYCLE and self.scenario.cycle.id == self.new_cycle_id:
            # Data node already exists. No need to duplicate.
            dn._parent_ids.update([task.id]) if task else dn._parent_ids.update([self.new_scenario.id])
            self.__data_manager._set(dn)
            Notifier.publish(_make_event(dn, EventOperation.UPDATE, "parent_ids", dn._parent_ids))
            return dn
        if dn.scope == Scope.CYCLE:
            existing_dns = self.__data_manager._repository._get_by_configs_and_owner_ids(  # type: ignore
                [(dn.config_id, self.new_cycle_id)],
                self.__data_manager._build_filters_with_version(None))
            if existing_dns.get((dn.config_id, self.new_cycle_id)):
                ex_dn = existing_dns[(dn.config_id, self.new_cycle_id)]
                # A cycle data node with same config and same cycle owner already exist. No need to duplicate it.
                ex_dn._parent_ids.update([task.id]) if task else ex_dn._parent_ids.update([self.new_scenario.id])
                self.__data_manager._set(ex_dn)
                Notifier.publish(_make_event(ex_dn, EventOperation.UPDATE, "parent_ids", ex_dn._parent_ids))
                return ex_dn

        new_dn = self.__init_new_datanode(dn, task)
        if new_dn._config_id in self.data_to_duplicate:
            duplicator = _DataDuplicator(dn)
            if duplicator.can_duplicate():
                duplicator.duplicate_data(new_dn)

        self.new_data_nodes[dn.config_id] = new_dn
        self.__data_manager._set(new_dn)
        Notifier.publish(_make_event(new_dn, EventOperation.CREATION))
        return new_dn

    def _duplicate_sequences(self):
        new_sequences = {}
        for seq_name, seq_data in self.scenario._sequences.items():
            new_sequence_id = Sequence._new_id(seq_name, self.new_scenario.id)
            new_sequence = {Scenario._SEQUENCE_PROPERTIES_KEY: seq_data[Scenario._SEQUENCE_PROPERTIES_KEY],
                            Scenario._SEQUENCE_TASKS_KEY: []}  # We do not want to duplicate the subscribers
            for task in seq_data[Scenario._SEQUENCE_TASKS_KEY]:
                new_task = self.new_tasks[task.config_id]
                new_task._parent_ids.update([new_sequence_id])
                self.__task_manager._set(new_task)
                new_sequence[Scenario._SEQUENCE_TASKS_KEY].append(self.new_tasks[task.config_id])
            new_sequences[seq_name] = new_sequence
        self.new_scenario._sequences = new_sequences

    def __init_new_scenario(self, new_creation_date: datetime, new_name: Optional[str]) -> Scenario:
        self.new_scenario = self.__scenario_manager._get(self.scenario)
        self.new_scenario.id = self.new_scenario._new_id(self.scenario.config_id)
        self.new_scenario._creation_date = new_creation_date
        if frequency:= Config.scenarios[self.scenario.config_id].frequency:
            cycle = self.__cycle_manager._get_or_create(frequency, new_creation_date)
            self.new_scenario._cycle = cycle
            self.new_scenario._primary_scenario = len(self.__scenario_manager._get_all_by_cycle(cycle)) == 0
            self.new_cycle_id = cycle.id
        else:
            self.new_scenario._primary_scenario = False
        if hasattr(self.new_scenario._properties, "_entity_owner"):
            self.new_scenario._properties._entity_owner = self.new_scenario
        if new_name:
            self.new_scenario._properties["name"] = new_name
        self.new_scenario._subscribers = _ListAttributes(self.new_scenario, [])

        self.new_scenario._tasks = set()  # To be potentially updated later
        self.new_scenario._sequences = {}  # To be potentially updated later
        self.new_scenario._additional_data_nodes = set()  # To be potentially updated later
        return self.new_scenario

    def __init_new_task(self, task: Task) -> Task:
        new_task = self.__task_manager._get(task)
        new_task.id = new_task._new_id(task.config_id)
        new_task._owner_id = self.__task_manager._get_owner_id(task.scope, self.new_cycle_id, self.new_scenario.id)
        new_task._parent_ids = {self.new_scenario.id}
        if hasattr(new_task._properties, "_entity_owner"):
            new_task._properties._entity_owner = new_task
        new_task._input = {}  # To be potentially updated later
        new_task._output = {}  # To be potentially updated later
        return new_task

    def __init_new_datanode(self, dn: DataNode, task: Optional[Task]=None) -> DataNode:
        new_dn = self.__data_manager._get(dn)
        new_dn.id = DataNode._new_id(dn._config_id)
        new_dn._owner_id = self.new_scenario.id if dn.scope == Scope.SCENARIO else self.new_cycle_id
        new_dn._parent_ids = {task.id} if task else {self.new_scenario.id}
        if hasattr(new_dn._properties, "_entity_owner"):
            new_dn._properties._entity_owner = new_dn
        new_dn._last_edit_date = None  # To be potentially updated later
        new_dn._edits = []  # To be potentially updated later
        return new_dn
