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

from typing import Callable, Dict, List, Optional, Union

from taipy import Gui, SubmissionStatus
from taipy.common.logger._taipy_logger import _TaipyLogger
from taipy.core.common._check_dependencies import EnterpriseEditionUtils
from taipy.core.common._utils import _load_fct
from taipy.core.config import DataNodeConfig, ScenarioConfig, TaskConfig
from taipy.core.notification import (
    Event,
    EventEntityType,
    EventOperation,
    Notifier,
    _Registration,
    _Topic,
)
from taipy.core.notification._core_event_consumer import _CoreEventConsumerBase
from taipy.event._event_callback import _Callback
from taipy.event._event_processor import _AbstractEventProcessor, _EventProcessor
from taipy.exceptions import NoGuiDefinedInEventConsumer


class EventConsumer(_CoreEventConsumerBase):
    """
    The Taipy event consumer service.

    This service listens for events in a Taipy application and triggers callbacks
    when events matching specific topics are produced. The main method to use is
    `on_event()^`, that registers a callback to a topic.

    Before starting the event consumer service, register each callback to a topic.
    The topics are defined by the entity type, the entity id, the operation, and the
    attribute name of the events. If an event matching the provided topic is produced,
    the callback execution is triggered.

    For more information about the event attributes please refer to the `Event^` class.

    !!! note "Filters"

        For each registered callback, you can specify a custom filter function in addition
        to the topic. This is mostly useful when your filter is more complex than the
        topic. The filter must accept an event as the only argument and return a
        boolean. If the filter returns False on an event, the callback is not triggered.
        See an example below.

    !!! note "Callback extra arguments"

        For each registered callback, you can also specify extra arguments to be passed to
        the callback function in addition to the event. The extra arguments must be provided
        as a list of values.

    !!! note "Broadcast a callback to all states"

        When registering a callback, you can specify if the callback is broadcast to all
        states of the GUI. In this case, the first argument of the callback must be the
        state and the second argument must be the event. Optionally, the callback can accept
        extra arguments (see the `callback_args` argument).
        In that case,
        If a `Gui^` ìnstance is provided, the callback is broadcast for all states of
        the GUI. In this case, the callbacks must accept the state as the first argument.

    !!! example

        === "One callback for all events"

            ```python
            from taipy import Event, EventConsumer

            def event_received(event: Event):
                print(f"Received event created at : {event.creation_date}")

            if __name__ == "__main__":
                event_consumer = EventConsumer()
                event_consumer.on_event(callback=event_received)
                event_consumer.start()
            ```

        === "Two callbacks for different topics"

            ```python
            from taipy import Event, EventConsumer

            def on_entity_creation(event: Event):
                print(f" {event.entity_type} entity created at {event.creation_date}")

            def on_scenario(event: Event):
                print(f"Scenario '{event.entity_id}' processed for a '{event.operation}' operation.")

            if __name__ == "__main__":
                event_consumer = EventConsumer()
                event_consumer.on_event(callback=on_entity_creation, operation=EventOperation.CREATION)
                event_consumer.on_event(callback=scenario_event, entity_type=EventEntityType.SCENARIO)
                event_consumer.start()
            ```

        === "Callbacks to be broadcast to all states"

            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui

            def event_received(state, event: Event):
                scenario = tp.get(event.entity_id)
                print(f"Received event created at : {event.creation_date} for scenario '{scenario.name}'.")

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_event(callback=event_received, broadcast=True)
                event_consumer.start()
                taipy.run(gui)
            ```

        === "With specific filters"

            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui

            def cycle_filter(event: Event):
                scenario = tp.get(event.entity_id)
                return scenario.cycle.name == "2023"

            def event_received(state, event: Event):
                scenario = tp.get(event.entity_id)
                cycle = scenario.cycle
                print(f"Received event for scenario '{scenario.name}' in cycle 'cycle.name'.")

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_event(
                    callback=event_received,
                    entity_type=EventEntityType.SCENARIO,
                    filter=cycle_filter,
                    broadcast=True)
                event_consumer.start()
                taipy.run(gui)
            ```

    Others methods such as `on_data_node_written()^` or `on_submission_finished()^` are
    utility methods as shortcuts to easily register callbacks for predefined topics and
    filters.
    """

    def __init__(self, gui: Gui = None) -> None:
        """Initialize the Event Consumer service.

        Arguments:
            gui (Optional[Gui]): The GUI instance used to broadcast the callbacks to all states.
        """
        self._registration = _Registration()
        self._topic_callbacks_map: Dict[_Topic, List[_Callback]] = {}
        self._gui = gui
        self.event_processor: _AbstractEventProcessor = _EventProcessor()
        if EnterpriseEditionUtils._using_enterprise():
            self.event_processor = _load_fct(
                EnterpriseEditionUtils._TAIPY_ENTERPRISE_EVENT_PACKAGE + "._event_processor",
                "_AuthorizedEventProcessor",
            )()
        super().__init__(self._registration.registration_id, self._registration.queue)

    def on_event(
        self,
        callback: Callable,
        callback_args: Optional[List] = None,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
        filter: Optional[Callable[[Event], bool]] = None,
        broadcast: Optional[bool] = False,
    ) -> 'EventConsumer':
        """Register a callback for a specific event.

        Arguments:
            callback (callable): The callback to be executed when the event is produced.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the first argument must be the state and the second argument must
                be the event. Otherwise, the first argument must be the event.
                Optionally, the callback can accept extra arguments (see the `callback_args`
                argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the event and possibly the state.
            entity_type (Optional[EventEntityType]): The entity type of the event.
                If None, the callback is registered for all entity types.
            entity_id (Optional[str]): The entity id of the event.
                If None, the callback is registered for all entities.
            operation (Optional[EventOperation]): The operation of the event.
                If None, the callback is registered for all operations.
            attribute_name (Optional[str]): The attribute name of an update event.
                If None, the callback is registered for all attribute names.
            filter (Optional[Callable[[Event], bool]]): A custom filter to apply to
                the event before triggering the callback. The filter must accept an event
                as the only argument and return a boolean. If the filter returns False, the
                callback is not triggered.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.
        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.
        """
        topic = self.__build_topic(entity_type, entity_id, operation, attribute_name)
        cb = self.__build_callback(callback, callback_args, filter, broadcast)
        self.__register_callback(topic, cb)
        return self

    def on_scenario_created(self,
                            callback: Callable,
                            callback_args: Optional[List]=None,
                            scenario_config: Union[str, ScenarioConfig, List, None]=None,
                            broadcast: Optional[bool]=False
                            ) -> 'EventConsumer':
        """Register a callback for scenario creation events.

        This method registers a callback for scenario creation events.

        !!! Examples:

                === "Two callbacks for all scenario creations"

                ```python
                import taipy as tp
                from taipy import Event, EventConsumer, Gui, State

                def print_scenario_created(event: Event, scenario: Scenario):
                    print(f"Scenario '{scenario.name}' created at '{event.creation_date}'.")

                def store_latest_scenario(state: State, event: Event, scenario: Scenario):
                    print(f"Scenario '{scenario.name}' created at '{event.creation_date}'.")
                    state.latest_scenario = scenario

                if __name__ == "__main__":
                    gui = Gui()
                    event_consumer = EventConsumer(gui)
                    event_consumer.on_scenario_created(callback=print_scenario_created)
                    event_consumer.on_scenario_created(callback=store_latest_scenario, broadcast=True)
                    event_consumer.start()
                    ...
                    taipy.run(gui)
                ```

                === "One callback for a specific scenario configuration"

                ```python
                import taipy as tp
                from taipy import Event, EventConsumer

                def print_scenario_created(event: Event, scenario: Scenario):
                    print(f"Scenario '{scenario.name}' created at '{event.creation_date}'.")


                if __name__ == "__main__":
                    event_consumer = EventConsumer()
                    event_consumer.on_scenario_created(callback=print_scenario_created, scenario_config="my_cfg")
                    event_consumer.start()
                    ...
                ```

        The callback is triggered when a scenario is created. If the `broadcast` argument
        is set to True, the callback is broadcast to all states of the GUI. The callback
        can also accept extra arguments (see the `callback_args` argument).

        Arguments:
            callback (callable): The callback to be executed when the event is produced.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the callback first argument must be a state, the second
                argument must be an event, and the third argument must be the scenario.
                Otherwise, the first argument must be an event and the second argument must
                be the scenario. Optionally, the callback can accept extra arguments (see
                the `callback_args` argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the state, the event, and the scenario.
            scenario_config (Union[str, ScenarioConfig, List, None]): The
                optional scenario configuration ids or scenario configurations
                for which the callback is registered. If None, the callback is registered
                for all scenario configurations.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.

        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.

        """
        scenario_config = self.__format_configs_parameter(ScenarioConfig, scenario_config)

        def _filter(event: Event) -> bool:
            import taipy as tp

            sc = tp.get(event.entity_id)
            if scenario_config and sc.config_id not in scenario_config:
                return False
            event.metadata["predefined_args"] = [sc]
            return True

        self.on_event(callback=callback,
                      callback_args=callback_args,
                      entity_type=EventEntityType.SCENARIO,
                      operation=EventOperation.CREATION,
                      filter=_filter,
                      broadcast=broadcast)
        return self

    def on_scenario_deleted(self,
                            callback: Callable,
                            callback_args: Optional[List]=None,
                            scenario_config: Union[str, ScenarioConfig, List, None] = None,
                            broadcast: Optional[bool]=False
                            ) -> 'EventConsumer':
        """ Register a callback for scenario deletion events.

        This method registers a callback for scenario deletion events.

        !!! Examples:

            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui, State

            def record_deletions(state: State, event: Event, scenario_id: str):
                print(f"Scenario deleted at '{event.creation_date}'.")
                state.deleted_scenarios.append[scenario_id]

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_scenario_deleted(callback=record_deletions, broadcast=True)
                event_consumer.start()
                ...
                taipy.run(gui)
            ```

        The callback is triggered when a scenario is deleted. If the `broadcast` argument
        is set to True, the callback is broadcast to all states of the GUI. The callback
        can also accept extra arguments (see the `callback_args` argument).

        Arguments:
            callback (callable): The callback to be executed when consuming an event.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the callback first argument must be a state, the second
                argument must be an event, and the third argument must be the scenario id.
                Otherwise, the first argument must be an event and the second argument must
                be the scenario id. Optionally, the callback can accept extra arguments (see
                the `callback_args` argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the state, the event, and the scenario id.
            scenario_config (Union[str, ScenarioConfig, List, None]): The
                optional scenario configuration ids or scenario configurations
                for which the callback is registered. If None, the callback is registered
                for all scenario configurations.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.

        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.

        """
        scenario_config = self.__format_configs_parameter(ScenarioConfig, scenario_config)

        def _filter(event: Event) -> bool:
            if not scenario_config:
                event.metadata["predefined_args"] = [event.entity_id]
                return True
            for cfg_id in scenario_config:
                if cfg_id in event.entity_id:
                    event.metadata["predefined_args"] = [event.entity_id]
                    return True
            return False

        self.on_event(callback=callback,
                      callback_args=callback_args,
                      entity_type=EventEntityType.SCENARIO,
                      operation=EventOperation.DELETION,
                      filter=_filter,
                      broadcast=broadcast)
        return self

    def on_datanode_written(self,
                            callback: Callable,
                            callback_args: Optional[List] = None,
                            datanode_config: Union[str, DataNodeConfig, List, None] = None,
                            broadcast: Optional[bool] = False
                            ) -> 'EventConsumer':
        """Register a callback for data node written events.

        This method registers a callback for datanode written events.

        !!! Examples:
            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui, State

            def last_data_edition(state: State, event: Event, datanode: Datanode, data: Any):
                print(f"Datanode written at '{event.creation_date}'.")
                state.last_data_edition.append[datanode.id]

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_datanode_written(callback=last_data_edition, broadcast=True)
                event_consumer.start()
                ...
                taipy.run(gui)
            ```

        The callback is triggered when a datanode is written (see methods
        `Datanode.write()^` or `Datanode.append()^`). If the `broadcast` argument
        is set to True, the callback is broadcast to all states of the GUI. The callback
        can also accept extra arguments (see the `callback_args` argument).


        Arguments:
            callback (callable): The callback to be executed when consuming an event.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the callback first argument must be a state, the second
                argument must be an event, the third argument must be the datanode, and the
                fourth argument must be the data. Otherwise, the first argument must be an
                event, the second argument must be the datanode, and the third argument must
                be the data. Optionally, the callback can accept extra arguments (see
                the `callback_args` argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the state, the event, the datanode, and the data.
            datanode_config (Union[str, DataNodeConfig, List, None]): The
                optional datanode configuration ids or datanode configurations
                for which the callback is registered. If None, the callback is registered
                for all datanode configurations.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.

        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.
        """
        datanode_config = self.__format_configs_parameter(DataNodeConfig, datanode_config)

        def _filter(event: Event) -> bool:
            import taipy as tp

            dn = tp.get(event.entity_id)
            if datanode_config and dn.config_id not in datanode_config:
                return False
            event.metadata["predefined_args"] = [dn, dn.read()]
            return True

        self.on_event(callback=callback,
                      callback_args=callback_args,
                      entity_type=EventEntityType.DATA_NODE,
                      operation=EventOperation.UPDATE,
                      attribute_name="last_edit_date",
                      filter=_filter,
                      broadcast=broadcast)
        return self

    def on_datanode_deleted(self,
                            callback: Callable,
                            callback_args: Optional[List] = None,
                            datanode_config: Union[str, DataNodeConfig, List, None] = None,
                            broadcast: Optional[bool] = False
                            ) -> 'EventConsumer':
        """ Register a callback for data node deletion events.

        This method registers a callback for datanode deletion events.

        !!! Examples:
            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui, State

            def record_deletions(state: State, event: Event, datanode_id: str):
                print(f"Datanode deleted at '{event.creation_date}'.")
                state.deleted_datanodes.append[datanode_id]

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_datanode_deleted(callback=record_deletions, broadcast=True)
                event_consumer.start()
                ...
                taipy.run(gui)
            ```

        The callback is triggered when a datanode is deleted. If the `broadcast` argument
        is set to True, the callback is broadcast to all states of the GUI. The callback
        can also accept extra arguments (see the `callback_args` argument).

        Arguments:
            callback (callable): The callback to be executed when consuming an event.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the callback first argument must be a state, the second
                argument must be an event, and the third argument must be the datanode id.
                Otherwise, the first argument must be an event and the second argument must
                be the datanode id. Optionally, the callback can accept extra arguments (see
                the `callback_args` argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the state, the event, and the datanode id.
            datanode_config (Union[str, DataNodeConfig, List, None]): The
                optional datanode configuration ids or datanode configurations
                for which the callback is registered. If None, the callback is registered
                for all datanode configurations.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.

        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.
        """
        datanode_config = self.__format_configs_parameter(DataNodeConfig, datanode_config)

        def _filter(event: Event) -> bool:
            if not datanode_config:
                event.metadata["predefined_args"] = [event.entity_id]
                return True
            for cfg_id in datanode_config:
                if cfg_id in event.entity_id:
                    event.metadata["predefined_args"] = [event.entity_id]
                    return True
            return False

        self.on_event(callback=callback,
                      callback_args=callback_args,
                      entity_type=EventEntityType.DATA_NODE,
                      operation=EventOperation.DELETION,
                      filter=_filter,
                      broadcast=broadcast)
        return self


    def on_datanode_created(self,
                            callback: Callable,
                            callback_args: Optional[List] = None,
                            datanode_config: Union[str, DataNodeConfig, List, None] = None,
                            broadcast: Optional[bool] = False
                            ) -> 'EventConsumer':
        """ Register a callback to be executed on data node creation event.

        This method registers a callback for datanode creation events.

        !!! Examples:
            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui, State

            def record_creations(state: State, event: Event, datanode_id: str):
                print(f"Datanode created at '{event.creation_date}'.")
                state.created_datanodes.append[datanode_id]

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_datanode_created(callback=record_creations, broadcast=True)
                event_consumer.start()
                ...
                taipy.run(gui)
            ```

        The callback is triggered when a datanode is created. If the `broadcast` argument
        is set to True, the callback is broadcast to all states of the GUI. The callback
        can also accept extra arguments (see the `callback_args` argument).

        Arguments:
            callback (callable): The callback to be executed when consuming an event.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the callback first argument must be a state, the second
                argument must be an event, and the third argument must be the datanode.
                Otherwise, the first argument must be an event and the second argument must
                be the datanode. Optionally, the callback can accept extra arguments (see
                the `callback_args` argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the state, the event, and the datanode.
            datanode_config (Union[str, ScenarioConfig, List, None]): The
                optional datanode configuration ids or datanode configurations
                for which the callback is registered. If None, the callback is registered
                for all datanode configurations.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.

        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.
        """
        datanode_config = self.__format_configs_parameter(DataNodeConfig, datanode_config)

        def _filter(event: Event) -> bool:
            import taipy as tp

            dn = tp.get(event.entity_id)
            if datanode_config and dn.config_id not in datanode_config:
                return False
            event.metadata["predefined_args"] = [dn]
            return True

        self.on_event(callback=callback,
                      callback_args=callback_args,
                      entity_type=EventEntityType.DATA_NODE,
                      operation=EventOperation.CREATION,
                      filter=_filter,
                      broadcast=broadcast)
        return self

    def on_submission_finished(self,
                               callback: Callable,
                               callback_args: Optional[List] = None,
                               config_ids: Union[str, ScenarioConfig, TaskConfig, List, None] = None,
                               broadcast: Optional[bool] = False
                               ) -> 'EventConsumer':
        """Register a callback for submission finished events.

        This method registers a callback for submission finished events.

        !!! Examples:
            ```python
            import taipy as tp
            from taipy import Event, EventConsumer, Gui, State

            def record_submissions(state: State, event: Event, submittable: Submittable, submission: Submission):
                print(f"Submission finished at '{event.creation_date}' with status '{submission.submission_status}'.")
                if submission.submission_status == SubmissionStatus.COMPLETED:
                    state.completed.append[submittable.id]
                elif submission.submission_status == SubmissionStatus.FAILED:
                    state.failed.append[submittable.id]

            if __name__ == "__main__":
                gui = Gui()
                event_consumer = EventConsumer(gui)
                event_consumer.on_submission_finished(callback=record_submissions, broadcast=True)
                event_consumer.start()
                ...
                taipy.run(gui)
            ```

        The callback is triggered when a submission is finished. If the `broadcast` argument
        is set to True, the callback is broadcast to all states of the GUI. The callback
        can also accept extra arguments (see the `callback_args` argument).

        Arguments:
            callback (callable): The callback to be executed when consuming an event.
                If the callback is executed for all states of the GUI (see the `broadcast`
                argument), the callback first argument must be a state, the second
                argument must be an event, the third argument must be the submittable, and
                the fourth argument must be the submission. Otherwise, the first argument
                must be an event and the second argument must be the submittable, and the
                third argument must be the submission. Optionally, the callback can accept
                extra arguments (see the `callback_args` argument).
            callback_args (List[AnyOf]): The extra arguments to be passed to the callback
                function in addition to the state, the event, the submittable, and the
                submission.
            config_ids (Union[str, ScenarioConfig, TaskConfig, List, None]): The
                optional scenario configuration ids or task configuration ids or scenario
                configurations or task configurations for which the callback is registered.
                If None, the callback is registered for any submittable.
            broadcast (Optional[bool]): If True, the callback is broadcast to all states
                of the GUI. A `Gui^` instance must have been provided to the EventConsumer
                constructor when the `broadcast` argument is True.<br/>
                If false, the callback is only triggered once for each event.

        Returns:
            EventConsumer: The current instance of the `EventConsumer` service.
        """
        if isinstance(config_ids, str):
            config_ids = [config_ids]
        if isinstance(config_ids, TaskConfig):
            config_ids = [config_ids.id]
        if isinstance(config_ids, ScenarioConfig):
            config_ids = [config_ids.id]
        if isinstance(config_ids, list):
            res = []
            for cfg in config_ids:
                if isinstance(cfg, TaskConfig):
                    res.append(cfg.id)
                elif isinstance(cfg, ScenarioConfig):
                    res.append(cfg.id)
                else:
                    res.append(cfg)
            config_ids = res

        def _filter(event: Event) -> bool:
            finished_statuses = {SubmissionStatus.COMPLETED, SubmissionStatus.FAILED, SubmissionStatus.CANCELED}
            if not event.attribute_value or event.attribute_value not in finished_statuses:
                return False
            import taipy as tp

            submission = tp.get(event.entity_id)
            if config_ids:
                # We are filtering on a specific config
                if not submission.entity_config_id:
                    # It is a submission for a sequence that does not have configs
                    return False
                if submission.entity_config_id not in config_ids:
                    # It is a submission for a config that is not in the list
                    return False
            submittable = tp.get(submission.entity_id)
            event.metadata["predefined_args"] = [submittable, submission]
            return True

        self.on_event(callback=callback,
                      callback_args=callback_args,
                      entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      attribute_name="submission_status",
                      filter=_filter,
                      broadcast=broadcast)
        return self

    def process_event(self, event: Event) -> None:
        """Process an event.

        This method is responsible for processing the incoming event. It should be implemented
        in subclasses to define the custom logic for handling events.

        Args:
            event (Event): The event to be processed.
        """
        self.event_processor.process_event(self, event)

    def start(self):
        """Start the event consumer thread."""
        Notifier._register_from_registration(self._registration)
        super().start()

    def stop(self):
        """Stop the event consumer thread."""
        super().stop()
        Notifier.unregister(self._registration.registration_id)

    @staticmethod
    def __format_configs_parameter(clazz, parameter) -> List[str]:
        if isinstance(parameter, str):
            parameter = [parameter]
        if isinstance(parameter, clazz):
            parameter = [parameter.id]  # type: ignore[attr-defined]
        if isinstance(parameter, list):
            parameter = [cfg.id if isinstance(cfg, clazz) else cfg for cfg in parameter] # type: ignore[attr-defined]
        return parameter

    def __build_topic(self, entity_type, entity_id, operation, attribute_name):
        topic = _Topic(entity_type, entity_id, operation, attribute_name)
        self._registration.add_topic(
            entity_type=topic.entity_type,
            entity_id=topic.entity_id,
            operation=topic.operation,
            attribute_name=topic.attribute_name
        )
        return topic

    def __build_callback(self, callback, callback_args, filter, broadcast):
        if broadcast and self._gui is None:
            _TaipyLogger._get_logger().error(
                "A callback is set to be broadcast to all states of "
                "the GUI but no GUI is provided to the event consumer."
            )
            raise NoGuiDefinedInEventConsumer()
        if callback_args is None:
            callback_args = []
        cb = _Callback(callback, args=callback_args, broadcast=broadcast, filter=filter)
        return cb

    def __register_callback(self, topic, cb):
        if self._topic_callbacks_map.get(topic) is None:
            self._topic_callbacks_map[topic] = []
        self._topic_callbacks_map[topic].append(cb)

    def _process_event(self, event: Event) -> None:
        for topic, cbs in self._topic_callbacks_map.items():
            if Notifier._is_matching(event, topic):
                for cb in cbs:
                    if not cb.filter or cb.filter(event):
                        self.__do_process(cb, event)

    def __do_process(self, cb, event: Event) -> None:
        predefined_args = event.metadata.pop("predefined_args", [])
        if cb.broadcast:
            if not self._gui:
                _TaipyLogger._get_logger().error(
                    "A callback is set to be broadcast to all states of "
                    "the GUI but no GUI is provided to the event consumer."
                )
                return
            self._gui.broadcast_callback(cb.callback, [event, *predefined_args, *cb.args])
        else:
            cb.callback(event, *predefined_args, *cb.args)
