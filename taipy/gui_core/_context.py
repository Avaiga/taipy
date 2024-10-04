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

import datetime
import json
import typing as t
import zoneinfo
from collections import defaultdict
from numbers import Number
from pathlib import Path
from threading import Lock

import pandas as pd
from dateutil import parser

from taipy.common.config import Config
from taipy.core import (
    Cycle,
    DataNode,
    DataNodeId,
    Job,
    JobId,
    Scenario,
    ScenarioId,
    Sequence,
    SequenceId,
    Submission,
    SubmissionId,
    cancel_job,
    create_scenario,
    delete_job,
    get_cycles_scenarios,
    get_data_nodes,
    get_jobs,
    is_deletable,
    is_editable,
    is_promotable,
    is_readable,
    is_submittable,
    set_primary,
)
from taipy.core import delete as core_delete
from taipy.core import get as core_get
from taipy.core import submit as core_submit
from taipy.core.data._file_datanode_mixin import _FileDataNodeMixin
from taipy.core.notification import CoreEventConsumerBase, EventEntityType
from taipy.core.notification.event import Event, EventOperation
from taipy.core.notification.notifier import Notifier
from taipy.core.reason import ReasonCollection
from taipy.core.submission.submission_status import SubmissionStatus
from taipy.core.taipy import can_create
from taipy.gui import Gui, State
from taipy.gui._warnings import _warn
from taipy.gui.gui import _DoNotUpdate
from taipy.gui.utils._map_dict import _MapDict

from ._adapters import (
    _EntityType,
    _get_entity_property,
    _GuiCoreDatanodeAdapter,
    _GuiCoreScenarioProperties,
    _invoke_action,
)
from .filters import CustomScenarioFilter


class _GuiCoreContext(CoreEventConsumerBase):
    __PROP_ENTITY_ID = "id"
    __PROP_ENTITY_COMMENT = "comment"
    __PROP_CONFIG_ID = "config"
    __PROP_DATE = "date"
    __PROP_ENTITY_NAME = "name"
    __PROP_SCENARIO_PRIMARY = "primary"
    __PROP_SCENARIO_TAGS = "tags"
    __ENTITY_PROPS = (__PROP_CONFIG_ID, __PROP_DATE, __PROP_ENTITY_NAME)
    __ACTION = "action"
    _CORE_CHANGED_NAME = "core_changed"

    def __init__(self, gui: Gui) -> None:
        self.gui = gui
        self.scenario_by_cycle: t.Optional[t.Dict[t.Optional[Cycle], t.List[Scenario]]] = None
        self.data_nodes_by_owner: t.Optional[t.Dict[t.Optional[str], t.List[DataNode]]] = None
        self.scenario_configs: t.Optional[t.List[t.Tuple[str, str]]] = None
        self.jobs_list: t.Optional[t.List[Job]] = None
        self.client_submission: t.Dict[str, SubmissionStatus] = {}
        # register to taipy core notification
        reg_id, reg_queue = Notifier.register()
        # locks
        self.lock = Lock()
        self.submissions_lock = Lock()
        # lazy_start
        self.__started = False
        # super
        super().__init__(reg_id, reg_queue)

    def __lazy_start(self):
        if self.__started:
            return
        self.__started = True
        self.start()

    def process_event(self, event: Event):
        self.__lazy_start()
        if event.entity_type is EventEntityType.SCENARIO:
            with self.gui._get_authorization(system=True):
                self.scenario_refresh(
                    event.entity_id
                    if event.operation is EventOperation.DELETION or is_readable(t.cast(ScenarioId, event.entity_id))
                    else None
                )
        elif event.entity_type is EventEntityType.SEQUENCE and event.entity_id:
            sequence = None
            try:
                with self.gui._get_authorization(system=True):
                    sequence = (
                        core_get(event.entity_id)
                        if event.operation is not EventOperation.DELETION
                        and is_readable(t.cast(SequenceId, event.entity_id))
                        else None
                    )
                    if sequence and hasattr(sequence, "parent_ids") and sequence.parent_ids:  # type: ignore
                        self.broadcast_core_changed({"scenario": list(sequence.parent_ids)})  # type: ignore
            except Exception as e:
                _warn(f"Access to sequence {event.entity_id} failed", e)
        elif event.entity_type is EventEntityType.JOB:
            with self.lock:
                self.jobs_list = None
            # no broadcast because the submission status will do the job
            if event.operation is EventOperation.DELETION:
                self.broadcast_core_changed({"jobs": True})
        elif event.entity_type is EventEntityType.SUBMISSION:
            self.submission_status_callback(event.entity_id, event)
        elif event.entity_type is EventEntityType.DATA_NODE:
            with self.lock:
                self.data_nodes_by_owner = None
            self.broadcast_core_changed(
                {"datanode": event.entity_id if event.operation != EventOperation.DELETION else True}
            )

    def broadcast_core_changed(self, payload: t.Dict[str, t.Any], client_id: t.Optional[str] = None):
        self.gui._broadcast(_GuiCoreContext._CORE_CHANGED_NAME, payload, client_id)

    def scenario_refresh(self, scenario_id: t.Optional[str]):
        with self.lock:
            self.scenario_by_cycle = None
            self.data_nodes_by_owner = None
        self.broadcast_core_changed({"scenario": scenario_id or True})

    def submission_status_callback(self, submission_id: t.Optional[str] = None, event: t.Optional[Event] = None):
        if not submission_id or not is_readable(t.cast(SubmissionId, submission_id)):
            return
        submission = None
        new_status = None
        payload: t.Optional[t.Dict[str, t.Any]] = None
        client_id: t.Optional[str] = None
        try:
            last_status = self.client_submission.get(submission_id)
            if not last_status:
                return

            submission = t.cast(Submission, core_get(submission_id))
            if not submission or not submission.entity_id:
                return

            payload = {}
            new_status = t.cast(SubmissionStatus, submission.submission_status)

            client_id = submission.properties.get("client_id")
            if client_id:
                running_tasks = {}
                with self.gui._get_authorization(client_id):
                    for job in submission.jobs:
                        job = job if isinstance(job, Job) else t.cast(Job, core_get(job))
                        running_tasks[job.task.id] = (
                            SubmissionStatus.RUNNING.value
                            if job.is_running()
                            else SubmissionStatus.PENDING.value
                            if job.is_pending()
                            else None
                        )
                    payload.update(tasks=running_tasks)

                    if last_status is not new_status:
                        # callback
                        submission_name = submission.properties.get("on_submission")
                        if submission_name:
                            self.gui.invoke_callback(
                                client_id,
                                submission_name,
                                [
                                    core_get(submission.id),
                                    {
                                        "submission_status": new_status.name,
                                        "submittable_entity": core_get(submission.entity_id),
                                        **(event.metadata if event else {}),
                                    },
                                ],
                                submission.properties.get("module_context"),
                            )

            with self.submissions_lock:
                if new_status in (
                    SubmissionStatus.COMPLETED,
                    SubmissionStatus.FAILED,
                    SubmissionStatus.CANCELED,
                ):
                    self.client_submission.pop(submission_id, None)
                else:
                    self.client_submission[submission_id] = new_status

        except Exception as e:
            _warn(f"Submission ({submission_id}) is not available", e)

        finally:
            if payload is not None:
                payload.update(jobs=True)
                entity_id = submission.entity_id if submission else None
                if entity_id:
                    payload.update(scenario=entity_id)
                    if new_status:
                        payload.update(submission=new_status.value)
                self.broadcast_core_changed(payload, client_id)

    def no_change_adapter(self, entity: t.List):
        return entity

    def cycle_adapter(self, cycle: Cycle, sorts: t.Optional[t.List[t.Dict[str, t.Any]]] = None):
        self.__lazy_start()
        try:
            if (
                isinstance(cycle, Cycle)
                and is_readable(cycle.id)
                and core_get(cycle.id) is not None
                and self.scenario_by_cycle
            ):
                return [
                    cycle.id,
                    cycle.get_simple_label(),
                    self.get_sorted_scenario_list(self.scenario_by_cycle.get(cycle, []), sorts),
                    _EntityType.CYCLE.value,
                    False,
                ]
        except Exception as e:
            _warn(
                f"Access to {type(cycle).__name__} " + f"({cycle.id if hasattr(cycle, 'id') else 'No_id'})" + " failed",
                e,
            )
        return None

    def scenario_adapter(self, scenario: Scenario):
        self.__lazy_start()
        if isinstance(scenario, (tuple, list)):
            return scenario
        try:
            if isinstance(scenario, Scenario) and is_readable(scenario.id) and core_get(scenario.id) is not None:
                return [
                    scenario.id,
                    scenario.get_simple_label(),
                    None,
                    _EntityType.SCENARIO.value,
                    scenario.is_primary,
                ]
        except Exception as e:
            _warn(
                f"Access to {type(scenario).__name__} "
                + f"({scenario.id if hasattr(scenario, 'id') else 'No_id'})"
                + " failed",
                e,
            )
        return None

    def filter_entities(
        self, cycle_scenario: t.List, col: str, col_type: str, is_dn: bool, action: str, val: t.Any, col_fn=None
    ):
        cycle_scenario[2] = [
            e for e in cycle_scenario[2] if _invoke_action(e, col, col_type, is_dn, action, val, col_fn)
        ]
        return cycle_scenario

    def adapt_scenarios(self, cycle: t.List):
        cycle[2] = [self.scenario_adapter(e) for e in cycle[2]]
        return cycle

    def get_sorted_scenario_list(
        self,
        entities: t.Union[t.List[t.Union[Cycle, Scenario]], t.List[Scenario]],
        sorts: t.Optional[t.List[t.Dict[str, t.Any]]],
    ):
        if sorts:
            sorted_list = entities
            for sd in reversed(sorts):
                col = sd.get("col", "")
                order = sd.get("order", True)
                sorted_list = sorted(sorted_list, key=_get_entity_property(col, Scenario, Cycle), reverse=not order)
        else:
            sorted_list = sorted(entities, key=_get_entity_property("creation_date", Scenario, Cycle))
        return [self.cycle_adapter(e, sorts) if isinstance(e, Cycle) else e for e in sorted_list]

    def get_filtered_scenario_list(
        self,
        entities: t.List[t.Union[t.List, Scenario, None]],
        filters: t.Optional[t.List[t.Dict[str, t.Any]]],
    ):
        if not filters:
            return entities
        # filtering
        filtered_list = list(entities)
        for fd in filters:
            col = fd.get("col", "")
            is_datanode_prop = _GuiCoreScenarioProperties.is_datanode_property(col)
            col_type = fd.get("type", "no type")
            col_fn = cp[0] if (cp := col.split("(")) and len(cp) > 1 else None
            val = fd.get("value")
            action = fd.get("action", "")
            customs = CustomScenarioFilter._get_custom(col)
            if customs:
                with self.gui._set_locals_context(customs[0] or None):
                    fn = self.gui._get_user_function(customs[1])
                    if callable(fn):
                        col = fn
            if (
                isinstance(col, str)
                and next(filter(lambda s: not s.isidentifier(), (col_fn or col).split(".")), False) is True
            ):
                _warn(f'Error filtering with "{col_fn or col}": not a valid Python identifier.')
                continue

            # level 1 filtering
            filtered_list = [
                e
                for e in filtered_list
                if not isinstance(e, Scenario)
                or _invoke_action(e, t.cast(str, col), col_type, is_datanode_prop, action, val, col_fn)
            ]
            # level 2 filtering
            filtered_list = [
                e
                if isinstance(e, Scenario)
                else self.filter_entities(
                    t.cast(list, e), t.cast(str, col), col_type, is_datanode_prop, action, val, col_fn
                )
                for e in filtered_list
            ]
        # remove empty cycles
        return [e for e in filtered_list if isinstance(e, Scenario) or (isinstance(e, (tuple, list)) and len(e[2]))]

    def get_scenarios(
        self,
        scenarios: t.Optional[t.List[t.Union[Cycle, Scenario]]],
        filters: t.Optional[t.List[t.Dict[str, t.Any]]],
        sorts: t.Optional[t.List[t.Dict[str, t.Any]]],
    ):
        self.__lazy_start()
        cycles_scenarios: t.List[t.Union[Cycle, Scenario]] = []
        with self.lock:
            # always needed to get scenarios for a cycle in cycle_adapter
            if self.scenario_by_cycle is None:
                self.scenario_by_cycle = get_cycles_scenarios()
            if scenarios is None:
                for cycle, c_scenarios in self.scenario_by_cycle.items():
                    if cycle is None:
                        cycles_scenarios.extend(c_scenarios)
                    else:
                        cycles_scenarios.append(cycle)
        if scenarios is not None:
            cycles_scenarios = scenarios
        adapted_list = self.get_sorted_scenario_list(cycles_scenarios, sorts)
        adapted_list = self.get_filtered_scenario_list(adapted_list, filters)
        return adapted_list

    def select_scenario(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 2:
            return
        state.assign(args[0], args[1])

    def get_scenario_by_id(self, id: str) -> t.Optional[Scenario]:
        self.__lazy_start()
        if not id or not is_readable(t.cast(ScenarioId, id)):
            return None
        try:
            return core_get(t.cast(ScenarioId, id))
        except Exception:
            return None

    def get_scenario_configs(self):
        self.__lazy_start()
        with self.lock:
            if self.scenario_configs is None:
                configs = Config.scenarios
                if isinstance(configs, dict):
                    self.scenario_configs = [(id, f"{c.id}") for id, c in configs.items() if id != "default"]
            return self.scenario_configs

    def crud_scenario(self, state: State, id: str, payload: t.Dict[str, str]):  # noqa: C901
        self.__lazy_start()
        args = payload.get("args")
        start_idx = 3
        if (
            args is None
            or not isinstance(args, list)
            or len(args) < start_idx + 3
            or not isinstance(args[start_idx], bool)
            or not isinstance(args[start_idx + 1], bool)
            or not isinstance(args[start_idx + 2], dict)
        ):
            return
        error_var = t.cast(str, payload.get("error_id"))
        update = args[start_idx]
        delete = args[start_idx + 1]
        data = t.cast(dict, args[start_idx + 2])
        with_dialog = True if len(args) < start_idx + 4 else bool(args[start_idx + 3])
        scenario = None
        user_scenario = None

        name = data.get(_GuiCoreContext.__PROP_ENTITY_NAME)
        if update:
            scenario_id = t.cast(ScenarioId, data.get(_GuiCoreContext.__PROP_ENTITY_ID))
            if delete:
                if not (reason := is_deletable(scenario_id)):
                    state.assign(error_var, f"Scenario. {scenario_id} is not deletable: {_get_reason(reason)}.")
                    return
                try:
                    core_delete(scenario_id)
                except Exception as e:
                    state.assign(error_var, f"Error deleting Scenario. {e}")
            else:
                if not self.__check_readable_editable(state, scenario_id, "Scenario", error_var):
                    return
                scenario = core_get(scenario_id)
        else:
            if with_dialog:
                config_id = data.get(_GuiCoreContext.__PROP_CONFIG_ID)
                scenario_config = Config.scenarios.get(config_id)
                if with_dialog and scenario_config is None:
                    state.assign(error_var, f"Invalid configuration id ({config_id})")
                    return
                date_str = data.get(_GuiCoreContext.__PROP_DATE)
                try:
                    date = parser.parse(date_str) if isinstance(date_str, str) else None
                except Exception as e:
                    state.assign(error_var, f"Invalid date ({date_str}).{e}")
                    return
            else:
                scenario_config = None
                date = None
            scenario_id = None
            gui = state.get_gui()
            try:
                on_creation = args[0] if isinstance(args[0], str) else None
                on_creation_function = gui._get_user_function(on_creation) if on_creation else None
                if callable(on_creation_function) and on_creation:
                    try:
                        res = gui._call_function_with_state(
                            on_creation_function,
                            [
                                id,
                                {
                                    "action": on_creation,
                                    "config": scenario_config,
                                    "date": date,
                                    "label": name,
                                    "properties": {v.get("key"): v.get("value") for v in data.get("properties", {})},
                                },
                            ],
                        )
                        if isinstance(res, Scenario):
                            # everything's fine
                            user_scenario = res
                            scenario_id = user_scenario.id
                            state.assign(error_var, "")
                            return
                        if res:
                            # do not create
                            state.assign(error_var, f"{res}")
                            return
                    except Exception as e:  # pragma: no cover
                        if not gui._call_on_exception(on_creation, e):
                            _warn(f"on_creation(): Exception raised in '{on_creation}()'", e)
                        state.assign(
                            error_var,
                            f"Error creating Scenario with '{on_creation}()'. {e}",
                        )
                        return
                elif on_creation is not None:
                    _warn(f"on_creation(): '{on_creation}' is not a function.")
                elif not with_dialog:
                    if len(Config.scenarios) == 2:
                        scenario_config = next(sc for k, sc in Config.scenarios.items() if k != "default")
                    else:
                        state.assign(
                            error_var,
                            "Error creating Scenario: only one scenario config needed "
                            + f"({len(Config.scenarios) - 1}) found.",
                        )
                        return
                scenario = create_scenario(scenario_config, date, name) if scenario_config else None
                scenario_id = scenario.id if scenario else None
            except Exception as e:
                state.assign(error_var, f"Error creating Scenario. {e}")
            finally:
                self.scenario_refresh(scenario_id)
                if (scenario or user_scenario) and (sel_scenario_var := args[1] if isinstance(args[1], str) else None):
                    try:
                        var_name, _ = gui._get_real_var_name(sel_scenario_var)
                        self.gui._update_var(var_name, scenario or user_scenario, on_change=args[2])
                    except Exception as e:  # pragma: no cover
                        _warn("Can't find value variable name in context", e)
        if scenario:
            if not (reason := is_editable(scenario)):
                state.assign(error_var, f"Scenario {scenario_id or name} is not editable: {_get_reason(reason)}.")
                return
            with scenario as sc:
                sc.properties[_GuiCoreContext.__PROP_ENTITY_NAME] = name
                if props := data.get("properties"):
                    try:
                        new_keys = [prop.get("key") for prop in props]
                        for key in t.cast(dict, sc.properties).keys():
                            if key and key not in _GuiCoreContext.__ENTITY_PROPS and key not in new_keys:
                                t.cast(dict, sc.properties).pop(key, None)
                        for prop in props:
                            key = prop.get("key")
                            if key and key not in _GuiCoreContext.__ENTITY_PROPS:
                                sc._properties[key] = prop.get("value")
                        state.assign(error_var, "")
                    except Exception as e:
                        state.assign(error_var, f"Error creating Scenario. {e}")

    @staticmethod
    def __assign_var(state: State, var_name: t.Optional[str], msg: str):
        if var_name:
            state.assign(var_name, msg)

    def edit_entity(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        error_var = payload.get("error_id")
        data = t.cast(dict, args[0])
        entity_id = t.cast(str, data.get(_GuiCoreContext.__PROP_ENTITY_ID))
        sequence = data.get("sequence")
        if not self.__check_readable_editable(state, entity_id, "Scenario", error_var):
            return
        scenario = t.cast(Scenario, core_get(entity_id))
        if scenario:
            try:
                if not sequence:
                    if isinstance(sequence, str) and (name := data.get(_GuiCoreContext.__PROP_ENTITY_NAME)):
                        scenario.add_sequence(name, t.cast(list, data.get("task_ids")))
                    else:
                        primary = data.get(_GuiCoreContext.__PROP_SCENARIO_PRIMARY)
                        if primary is True:
                            if not (reason := is_promotable(scenario)):
                                _GuiCoreContext.__assign_var(
                                    state, error_var, f"Scenario {entity_id} is not promotable: {_get_reason(reason)}."
                                )
                                return
                            set_primary(scenario)
                        self.__edit_properties(scenario, data)
                else:
                    if data.get("del", False):
                        scenario.remove_sequence(sequence)
                    else:
                        name = t.cast(str, data.get(_GuiCoreContext.__PROP_ENTITY_NAME))
                        if sequence != name:
                            scenario.rename_sequence(sequence, name)
                        if seqEntity := scenario.sequences.get(name):
                            seqEntity.tasks = t.cast(list, data.get("task_ids"))
                            self.__edit_properties(seqEntity, data)
                        else:
                            _GuiCoreContext.__assign_var(
                                state,
                                error_var,
                                f"Sequence {name} is not available in Scenario {entity_id}.",
                            )
                            return

                _GuiCoreContext.__assign_var(state, error_var, "")
            except Exception as e:
                _GuiCoreContext.__assign_var(state, error_var, f"Error updating {type(scenario).__name__}. {e}")

    def submit_entity(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = t.cast(dict, args[0])
        error_var = payload.get("error_id")
        try:
            scenario_id = t.cast(str, data.get(_GuiCoreContext.__PROP_ENTITY_ID))
            entity = t.cast(Scenario, core_get(scenario_id))
            if sequence := t.cast(str, data.get("sequence")):
                entity = t.cast(Sequence, entity.sequences.get(sequence))

            if not (reason := is_submittable(entity)):
                _GuiCoreContext.__assign_var(
                    state,
                    error_var,
                    f"{'Sequence' if sequence else 'Scenario'} {sequence or scenario_id} is not submittable: "
                    + f"{_get_reason(reason)}.",
                )
                return
            if entity:
                on_submission = data.get("on_submission_change")
                submission_entity = core_submit(
                    entity,
                    on_submission=on_submission,
                    client_id=self.gui._get_client_id(),
                    module_context=self.gui._get_locals_context(),
                )
                with self.submissions_lock:
                    self.client_submission[submission_entity.id] = submission_entity.submission_status
                if Config.core.mode == "development":
                    with self.submissions_lock:
                        self.client_submission[submission_entity.id] = SubmissionStatus.SUBMITTED
                    self.submission_status_callback(submission_entity.id)
                _GuiCoreContext.__assign_var(state, error_var, "")
        except Exception as e:
            _GuiCoreContext.__assign_var(state, error_var, f"Error submitting entity. {e}")

    def get_filtered_datanode_list(
        self,
        entities: t.List[t.Union[t.List, DataNode, None]],
        filters: t.Optional[t.List[t.Dict[str, t.Any]]],
    ):
        if not filters or not entities:
            return entities
        # filtering
        filtered_list = list(entities)
        for fd in filters:
            col = fd.get("col", "")
            col_type = fd.get("type", "no type")
            col_fn = cp[0] if (cp := col.split("(")) and len(cp) > 1 else None
            val = fd.get("value")
            action = fd.get("action", "")
            customs = CustomScenarioFilter._get_custom(col)
            if customs:
                with self.gui._set_locals_context(customs[0] or None):
                    fn = self.gui._get_user_function(customs[1])
                    if callable(fn):
                        col = fn
            if (
                isinstance(col, str)
                and next(filter(lambda s: not s.isidentifier(), (col_fn or col).split(".")), False) is True
            ):
                _warn(f'Error filtering with "{col_fn or col}": not a valid Python identifier.')
                continue
            # level 1 filtering
            filtered_list = [
                e
                for e in filtered_list
                if not isinstance(e, DataNode)
                or _invoke_action(e, t.cast(str, col), col_type, False, action, val, col_fn)
            ]
            # level 3 filtering
            filtered_list = [
                e
                if isinstance(e, DataNode)
                else self.filter_entities(d, t.cast(str, col), col_type, False, action, val, col_fn)
                for e in filtered_list
                for d in t.cast(list, t.cast(list, e)[2])
            ]
        # remove empty cycles
        return [e for e in filtered_list if isinstance(e, DataNode) or (isinstance(e, (tuple, list)) and len(e[2]))]

    def get_sorted_datanode_list(
        self,
        entities: t.Union[
            t.List[t.Union[Cycle, Scenario, DataNode]], t.List[t.Union[Scenario, DataNode]], t.List[DataNode]
        ],
        sorts: t.Optional[t.List[t.Dict[str, t.Any]]],
        adapt_dn=False,
    ):
        if not entities:
            return entities
        if sorts:
            sorted_list = entities
            for sd in reversed(sorts):
                col = sd.get("col", "")
                order = sd.get("order", True)
                sorted_list = sorted(sorted_list, key=_get_entity_property(col, DataNode), reverse=not order)
        else:
            sorted_list = entities
        return [self.data_node_adapter(e, sorts, adapt_dn) for e in sorted_list]

    def __do_datanodes_tree(self):
        if self.data_nodes_by_owner is None:
            self.data_nodes_by_owner = defaultdict(list)
            for dn in get_data_nodes():
                self.data_nodes_by_owner[dn.owner_id].append(dn)

    def get_datanodes_tree(
        self,
        scenarios: t.Optional[t.Union[Scenario, t.List[Scenario]]],
        datanodes: t.Optional[t.List[DataNode]],
        filters: t.Optional[t.List[t.Dict[str, t.Any]]],
        sorts: t.Optional[t.List[t.Dict[str, t.Any]]],
    ):
        self.__lazy_start()
        base_list = []
        with self.lock:
            self.__do_datanodes_tree()
        if datanodes is None:
            if scenarios is None:
                base_list = (self.data_nodes_by_owner or {}).get(None, []) + (
                    self.get_scenarios(None, None, None) or []
                )
            else:
                if isinstance(scenarios, (list, tuple)) and len(scenarios) > 1:
                    base_list = list(scenarios)
                else:
                    if self.data_nodes_by_owner:
                        owners = scenarios if isinstance(scenarios, (list, tuple)) else [scenarios]
                        base_list = [d for owner in owners for d in (self.data_nodes_by_owner).get(owner.id, [])]
                    else:
                        base_list = []
        else:
            base_list = datanodes
        adapted_list = self.get_sorted_datanode_list(t.cast(list, base_list), sorts)
        return self.get_filtered_datanode_list(t.cast(list, adapted_list), filters)

    def data_node_adapter(
        self,
        data: t.Union[Cycle, Scenario, Sequence, DataNode],
        sorts: t.Optional[t.List[t.Dict[str, t.Any]]] = None,
        adapt_dn=True,
    ):
        self.__lazy_start()
        if isinstance(data, tuple):
            raise NotImplementedError
        if isinstance(data, list):
            if data[2] and isinstance(t.cast(list, data[2])[0], (Cycle, Scenario, Sequence, DataNode)):
                data[2] = self.get_sorted_datanode_list(t.cast(list, data[2]), sorts, False)
            return data
        try:
            if hasattr(data, "id") and is_readable(data.id) and core_get(data.id) is not None:
                if isinstance(data, DataNode):
                    return (
                        [data.id, data.get_simple_label(), None, _EntityType.DATANODE.value, False]
                        if adapt_dn
                        else data
                    )

                with self.lock:
                    self.__do_datanodes_tree()
                if self.data_nodes_by_owner:
                    if isinstance(data, Cycle):
                        return [
                            data.id,
                            data.get_simple_label(),
                            self.get_sorted_datanode_list(
                                self.data_nodes_by_owner.get(data.id, [])
                                + (self.scenario_by_cycle or {}).get(data, []),
                                sorts,
                                False,
                            ),
                            _EntityType.CYCLE.value,
                            False,
                        ]
                    elif isinstance(data, Scenario):
                        return [
                            data.id,
                            data.get_simple_label(),
                            self.get_sorted_datanode_list(
                                t.cast(list, self.data_nodes_by_owner.get(data.id, []) + list(data.sequences.values())),
                                sorts,
                                False,
                            ),
                            _EntityType.SCENARIO.value,
                            data.is_primary,
                        ]
                    elif isinstance(data, Sequence):
                        if datanodes := self.data_nodes_by_owner.get(data.id):
                            return [
                                data.id,
                                data.get_simple_label(),
                                self.get_sorted_datanode_list(datanodes, sorts, False),
                                _EntityType.SEQUENCE.value,
                            ]
        except Exception as e:
            _warn(
                f"Access to {type(data)} ({data.id if hasattr(data, 'id') else 'No_id'}) failed",
                e,
            )

        return None

    def get_jobs_list(self):
        self.__lazy_start()
        with self.lock:
            if self.jobs_list is None:
                self.jobs_list = get_jobs()
            return self.jobs_list

    def job_adapter(self, job):
        self.__lazy_start()
        try:
            if hasattr(job, "id") and is_readable(job.id) and core_get(job.id) is not None:
                if isinstance(job, Job):
                    entity = core_get(job.owner_id)
                    return (
                        job.id,
                        job.get_simple_label(),
                        [],
                        entity.id if entity else "",
                        entity.get_simple_label() if entity else "",
                        job.submit_id,
                        job.creation_date,
                        job.status.value,
                        _get_reason(is_deletable(job)),
                        _get_reason(is_readable(job)),
                        _get_reason(is_editable(job)),
                    )
        except Exception as e:
            _warn(f"Access to job ({job.id if hasattr(job, 'id') else 'No_id'}) failed", e)
        return None

    def act_on_jobs(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = t.cast(dict, args[0])
        job_ids = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        job_action = data.get(_GuiCoreContext.__ACTION)
        if job_action and isinstance(job_ids, list):
            errs = []
            if job_action == "delete":
                for job_id in job_ids:
                    if not (reason := is_readable(job_id)):
                        errs.append(f"Job {job_id} is not readable: {_get_reason(reason)}.")
                        continue
                    if not (reason := is_deletable(job_id)):
                        errs.append(f"Job {job_id} is not deletable: {_get_reason(reason)}.")
                        continue
                    try:
                        delete_job(core_get(job_id))
                    except Exception as e:
                        errs.append(f"Error deleting job. {e}")
            elif job_action == "cancel":
                for job_id in job_ids:
                    if not (reason := is_readable(job_id)):
                        errs.append(f"Job {job_id} is not readable: {_get_reason(reason)}.")
                        continue
                    if not (reason := is_editable(job_id)):
                        errs.append(f"Job {job_id} is not cancelable: {_get_reason(reason)}.")
                        continue
                    try:
                        cancel_job(job_id)
                    except Exception as e:
                        errs.append(f"Error canceling job. {e}")
            _GuiCoreContext.__assign_var(state, payload.get("error_id"), "<br/>".join(errs) if errs else "")

    def get_job_details(self, job_id: t.Optional[JobId]):
        try:
            if job_id and is_readable(job_id) and (job := core_get(job_id)) is not None:
                if isinstance(job, Job):
                    entity = core_get(job.owner_id)
                    return (
                        job.id,
                        job.get_simple_label(),
                        entity.id if entity else "",
                        entity.get_simple_label() if entity else "",
                        job.submit_id,
                        job.creation_date,
                        job.status.value,
                        _get_reason(is_deletable(job)),
                        ""
                        if job.execution_duration is None
                        else str(datetime.timedelta(seconds=job.execution_duration)),
                        [] if job.stacktrace is None else job.stacktrace,
                    )
        except Exception as e:
            _warn(f"Access to job ({job_id}) failed", e)
        return None

    def edit_data_node(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        error_var = payload.get("error_id")
        data = t.cast(dict, args[0])
        entity_id = t.cast(str, data.get(_GuiCoreContext.__PROP_ENTITY_ID))
        if not self.__check_readable_editable(state, entity_id, "DataNode", error_var):
            return
        entity = t.cast(DataNode, core_get(entity_id))
        if isinstance(entity, DataNode):
            try:
                self.__edit_properties(entity, data)
                _GuiCoreContext.__assign_var(state, error_var, "")
            except Exception as e:
                _GuiCoreContext.__assign_var(state, error_var, f"Error updating Data node. {e}")

    def lock_datanode_for_edit(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = t.cast(dict, args[0])
        error_var = payload.get("error_id")
        entity_id = t.cast(str, data.get(_GuiCoreContext.__PROP_ENTITY_ID))
        if not self.__check_readable_editable(state, entity_id, "Data node", error_var):
            return
        lock = data.get("lock", True)
        entity = t.cast(DataNode, core_get(entity_id))
        if isinstance(entity, DataNode):
            try:
                if lock:
                    entity.lock_edit(self.gui._get_client_id())
                else:
                    entity.unlock_edit(self.gui._get_client_id())
                _GuiCoreContext.__assign_var(state, error_var, "")
            except Exception as e:
                _GuiCoreContext.__assign_var(state, error_var, f"Error locking Data node. {e}")

    def __edit_properties(self, entity: t.Union[Scenario, Sequence, DataNode], data: t.Dict[str, str]):
        with entity as ent:
            if isinstance(ent, Scenario):
                tags = data.get(_GuiCoreContext.__PROP_SCENARIO_TAGS)
                if isinstance(tags, (list, tuple)):
                    ent.tags = set(tags)
            name = data.get(_GuiCoreContext.__PROP_ENTITY_NAME)
            if isinstance(name, str):
                if hasattr(ent, _GuiCoreContext.__PROP_ENTITY_NAME):
                    setattr(ent, _GuiCoreContext.__PROP_ENTITY_NAME, name)
                else:
                    ent.properties[_GuiCoreContext.__PROP_ENTITY_NAME] = name
            props = data.get("properties")
            if isinstance(props, (list, tuple)):
                for prop in props:
                    key = t.cast(dict, prop).get("key")
                    if key and key not in _GuiCoreContext.__ENTITY_PROPS:
                        ent.properties[key] = t.cast(dict, prop).get("value")
            deleted_props = data.get("deleted_properties")
            if isinstance(deleted_props, (list, tuple)):
                for prop in deleted_props:
                    key = t.cast(dict, prop).get("key")
                    if key and key not in _GuiCoreContext.__ENTITY_PROPS:
                        ent.properties.pop(key, None)

    def get_scenarios_for_owner(self, owner_id: str):
        self.__lazy_start()
        cycles_scenarios: t.List[t.Union[Scenario, Cycle]] = []
        with self.lock:
            if self.scenario_by_cycle is None:
                self.scenario_by_cycle = get_cycles_scenarios()
            if owner_id:
                if owner_id == "GLOBAL":
                    for cycle, scenarios in self.scenario_by_cycle.items():
                        if cycle is None:
                            cycles_scenarios.extend(scenarios)
                        else:
                            cycles_scenarios.append(cycle)
                elif is_readable(t.cast(ScenarioId, owner_id)):
                    entity = core_get(owner_id)
                    if entity and (scenarios_cycle := self.scenario_by_cycle.get(t.cast(Cycle, entity))):
                        cycles_scenarios.extend(scenarios_cycle)
                    elif isinstance(entity, Scenario):
                        cycles_scenarios.append(entity)
        return sorted(cycles_scenarios, key=_get_entity_property("creation_date", Scenario))

    def get_data_node_history(self, id: str):
        self.__lazy_start()
        if id and (dn := core_get(id)) and isinstance(dn, DataNode):
            res = []
            for e in dn.edits:
                job_id = e.get("job_id")
                job: t.Optional[Job] = None
                if job_id:
                    if not (reason := is_readable(job_id)):
                        job_id += f" is not readable: {_get_reason(reason)}."
                    else:
                        job = core_get(job_id)
                res.append(
                    (
                        e.get("timestamp"),
                        job_id if job_id else e.get("writer_identifier", ""),
                        f"Execution of task {job.task.get_simple_label()}."
                        if job and job.task
                        else e.get("comment", ""),
                    )
                )
            return sorted(res, key=lambda r: r[0], reverse=True)
        return _DoNotUpdate()

    def __check_readable_editable(self, state: State, id: str, ent_type: str, var: t.Optional[str]):
        if not (reason := is_readable(t.cast(ScenarioId, id))):
            _GuiCoreContext.__assign_var(state, var, f"{ent_type} {id} is not readable: {_get_reason(reason)}.")
            return False
        if not (reason := is_editable(t.cast(ScenarioId, id))):
            _GuiCoreContext.__assign_var(state, var, f"{ent_type} {id} is not editable: {_get_reason(reason)}.")
            return False
        return True

    def update_data(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = t.cast(dict, args[0])
        error_var = payload.get("error_id")
        entity_id = t.cast(str, data.get(_GuiCoreContext.__PROP_ENTITY_ID))
        if not self.__check_readable_editable(state, entity_id, "Data node", error_var):
            return
        entity = t.cast(DataNode, core_get(entity_id))
        if isinstance(entity, DataNode):
            try:
                val = t.cast(str, data.get("value"))
                entity.write(
                    parser.parse(val)
                    if data.get("type") == "date"
                    else int(val)
                    if data.get("type") == "int"
                    else float(val)
                    if data.get("type") == "float"
                    else data.get("value"),
                    comment=t.cast(dict, data.get(_GuiCoreContext.__PROP_ENTITY_COMMENT)),
                )
                entity.unlock_edit(self.gui._get_client_id())
                _GuiCoreContext.__assign_var(state, error_var, "")
            except Exception as e:
                _GuiCoreContext.__assign_var(state, error_var, f"Error updating Data node value. {e}")
            _GuiCoreContext.__assign_var(state, payload.get("data_id"), entity_id)  # this will update the data value

    def tabular_data_edit(self, state: State, var_name: str, payload: dict):  # noqa:C901
        self.__lazy_start()
        error_var = payload.get("error_id")
        user_data = payload.get("user_data", {})
        dn_id = user_data.get("dn_id")
        if not self.__check_readable_editable(state, dn_id, "Data node", error_var):
            return
        datanode = core_get(dn_id) if dn_id else None
        if isinstance(datanode, DataNode):
            try:
                idx = t.cast(int, payload.get("index"))
                col = t.cast(str, payload.get("col"))
                tz = payload.get("tz")
                val = (
                    parser.parse(str(payload.get("value"))).astimezone(zoneinfo.ZoneInfo(tz)).replace(tzinfo=None)
                    if tz is not None
                    else payload.get("value")
                )
                # user_value = payload.get("user_value")
                data = self.__read_tabular_data(datanode)
                new_data: t.Any = None
                if isinstance(data, (pd.DataFrame, pd.Series)):
                    if isinstance(data, pd.DataFrame):
                        data.at[idx, col] = val
                    elif isinstance(data, pd.Series):
                        data.at[idx] = val
                    new_data = data
                elif isinstance(data, (dict, _MapDict)):
                    row = data.get(col, None)
                    data_tuple = False
                    if isinstance(row, tuple):
                        row = list(row)
                        data_tuple = True
                    if isinstance(row, list):
                        row[idx] = val
                        if data_tuple:
                            data[col] = tuple(row)
                        new_data = data
                    else:
                        _GuiCoreContext.__assign_var(
                            state,
                            error_var,
                            "Error updating Data node: dict values must be list or tuple.",
                        )
                else:
                    data_tuple = False
                    if isinstance(data, tuple):
                        data_tuple = True
                        data = list(data)
                    if isinstance(data, list):
                        row = data[idx]
                        row_tuple = False
                        if isinstance(row, tuple):
                            row = list(row)
                            row_tuple = True
                        if isinstance(row, list):
                            row[int(col)] = val
                            if row_tuple:
                                data[idx] = tuple(row)
                            new_data = data
                        elif col == "0" and (isinstance(row, (str, Number)) or "date" in type(row).__name__):
                            data[idx] = val
                            new_data = data
                        else:
                            _GuiCoreContext.__assign_var(
                                state,
                                error_var,
                                "Error updating data node: cannot handle multi-column list value.",
                            )
                        if data_tuple and new_data is not None:
                            new_data = tuple(new_data)
                    else:
                        _GuiCoreContext.__assign_var(
                            state,
                            error_var,
                            "Error updating data node tabular value: type does not support at[] indexer.",
                        )
                if new_data is not None:
                    datanode.write(new_data, comment=user_data.get(_GuiCoreContext.__PROP_ENTITY_COMMENT))
                    _GuiCoreContext.__assign_var(state, error_var, "")
            except Exception as e:
                _GuiCoreContext.__assign_var(state, error_var, f"Error updating data node tabular value. {e}")
        _GuiCoreContext.__assign_var(state, payload.get("data_id"), dn_id)

    def get_data_node_properties(self, id: str):
        self.__lazy_start()
        if id and is_readable(t.cast(DataNodeId, id)) and (dn := core_get(id)) and isinstance(dn, DataNode):
            try:
                return (
                    (
                        (k, f"{v}")
                        for k, v in dn._get_user_properties().items()
                        if k != _GuiCoreContext.__PROP_ENTITY_NAME
                    ),
                )
            except Exception:
                return None
        return None

    def __read_tabular_data(self, datanode: DataNode):
        return datanode.read()

    def get_data_node_tabular_data(self, id: str):
        self.__lazy_start()
        if id and is_readable(t.cast(DataNodeId, id)) and (dn := core_get(id)) and isinstance(dn, DataNode):
            if dn.is_ready_for_reading or (dn.edit_in_progress and dn.editor_id == self.gui._get_client_id()):
                try:
                    value = self.__read_tabular_data(dn)
                    if _GuiCoreDatanodeAdapter._is_tabular_data(dn, value):
                        return value
                except Exception:
                    return None
        return None

    def get_data_node_tabular_columns(self, id: str):
        self.__lazy_start()
        if id and is_readable(t.cast(DataNodeId, id)) and (dn := core_get(id)) and isinstance(dn, DataNode):
            if dn.is_ready_for_reading or (dn.edit_in_progress and dn.editor_id == self.gui._get_client_id()):
                try:
                    value = self.__read_tabular_data(dn)
                    if _GuiCoreDatanodeAdapter._is_tabular_data(dn, value):
                        return self.gui._tbl_cols(
                            True, True, "{}", json.dumps({"data": "tabular_data"}), tabular_data=value
                        )
                except Exception:
                    return None
        return None

    def get_data_node_chart_config(self, id: str):
        self.__lazy_start()
        if id and is_readable(t.cast(DataNodeId, id)) and (dn := core_get(id)) and isinstance(dn, DataNode):
            if dn.is_ready_for_reading or (dn.edit_in_progress and dn.editor_id == self.gui._get_client_id()):
                try:
                    return self.gui._chart_conf(
                        True,
                        True,
                        "{}",
                        json.dumps({"data": "tabular_data"}),
                        tabular_data=self.__read_tabular_data(dn),
                    )
                except Exception:
                    return None
        return None

    def on_dag_select(self, state: State, id: str, payload: t.Dict[str, str]):
        self.__lazy_start()
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 2:
            return
        on_action_function = self.gui._get_user_function(args[1]) if args[1] else None
        if callable(on_action_function):
            try:
                entity = (
                    core_get(args[0])
                    if (reason := is_readable(t.cast(ScenarioId, args[0])))
                    else f"{args[0]} is not readable: {_get_reason(reason)}"
                )
                self.gui._call_function_with_state(
                    on_action_function,
                    [entity],
                )
            except Exception as e:
                if not self.gui._call_on_exception(args[1], e):
                    _warn(f"dag.on_action(): Exception raised in '{args[1]}()' with '{args[0]}'", e)
        elif args[1]:
            _warn(f"dag.on_action(): Invalid function '{args[1]}()'.")

    def get_creation_reason(self):
        self.__lazy_start()
        return "" if (reason := can_create()) else f"Cannot create scenario: {_get_reason(reason)}"

    def on_file_action(self, state: State, id: str, payload: t.Dict[str, t.Any]):
        args = t.cast(list, payload.get("args"))
        act_payload = t.cast(t.Dict[str, str], args[0])
        dn_id = t.cast(DataNodeId, act_payload.get("id"))
        error_id = act_payload.get("error_id", "")
        if reason := is_readable(dn_id):
            try:
                dn = t.cast(_FileDataNodeMixin, core_get(dn_id))
                if act_payload.get("action") == "export":
                    path = dn._get_downloadable_path()
                    if path:
                        self.gui._download(Path(path), dn_id)
                    else:
                        reason = dn.is_downloadable()
                        state.assign(
                            error_id,
                            "Data unavailable: "
                            + ("The data node has never been written." if reason else reason.reasons),
                        )
                else:
                    checker_name = act_payload.get("upload_check")
                    checker = self.gui._get_user_function(checker_name) if checker_name else None
                    if not (
                        reason := dn._upload(
                            act_payload.get("path", ""),
                            t.cast(t.Callable[[str, t.Any], bool], checker) if callable(checker) else None,
                        )
                    ):
                        state.assign(error_id, f"Data unavailable: {reason.reasons}")

            except Exception as e:
                state.assign(error_id, f"Data node download error: {e}")
        else:
            state.assign(error_id, reason.reasons)


def _get_reason(reason: t.Union[bool, ReasonCollection]):
    return reason.reasons if isinstance(reason, ReasonCollection) else " "
