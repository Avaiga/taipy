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
from unittest import mock
from unittest.mock import ANY

from taipy import Gui
from taipy.core.config import DataNodeConfig
from taipy.core.notification import Event, EventEntityType, EventOperation
from taipy.event.event_processor import EventProcessor


def cb_0(event: Event, datanode: str):
    ...


def cb_1(event: Event, datanode: str, extra:str):
    ...


def cb_for_state(state, event: Event, datanode: str):
    ...


def test_on_datanode_deleted(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_deleted(callback=cb_0)
        # test the on_datanode_deleted method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    operation=EventOperation.DELETION,
                                    entity_type=EventEntityType.DATA_NODE,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.DELETION, entity_id=data_node.id)
        assert actual_filter is not None
        filter_value = actual_filter(event)
        assert filter_value is True  # No config provided, so the datanode passes the filter
        assert event.metadata["predefined_args"] == [data_node.id]


def test_on_datanode_deleted_multiple_configs(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_deleted(callback=cb_0,
                                     datanode_config=[DataNodeConfig("dn0"), "dn1", DataNodeConfig("dn2"), "data_node"])
        # test the on_datanode_deleted method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.DELETION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.DELETION, entity_id=data_node.id)
        assert actual_filter is not None
        filter_value = actual_filter(event)
        assert filter_value is True  # The datanode is from config 'data_node', so the datanode passes the filter
        assert event.metadata["predefined_args"] == [data_node.id]


def test_on_datanode_deleted_multiple_configs_no_matching(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_deleted(callback=cb_0,
                                     datanode_config=[DataNodeConfig("dn0"), "dn1"])
        # test the on_datanode_deleted method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.DELETION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.DELETION,
                      entity_id=data_node.id)
        assert actual_filter is not None
        f_val = actual_filter(event)
        assert not f_val  # Datanode is not from any of the provided configs, so it should not pass the filter
        assert event.metadata.get("predefined_args") is None


def test_on_datanode_deleted_with_args_and_matching_config(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_deleted(callback=cb_1, callback_args=["foo"], datanode_config="data_node")
        # test the on_datanode_deleted method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_1,
                                    callback_args=["foo"],
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.DELETION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.DELETION, entity_id=data_node.id)
        filter_value = actual_filter(event)
        assert filter_value is True # datanode is from config 'data_node', so the datanode passes the filter
        assert event.metadata.get("predefined_args") == [data_node.id]


def test_on_datanode_deleted_with_args_and_not_matching_config(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_deleted(callback=cb_1, callback_args=["foo"], datanode_config="WRONG_CFG")
        # test the on_datanode_deleted method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_1,
                                    callback_args=["foo"],
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.DELETION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.DELETION, entity_id=data_node.id)
        filter_value = actual_filter(event)
        assert filter_value is False  # The datanode is not from WRONG_CFG, so it should not pass the filter
        assert event.metadata.get("predefined_args") is None # No need to cache the datanode in the metadata


def test_on_datanode_deleted_with_broadcast(data_node):
    consumer = EventProcessor(Gui())
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.broadcast_on_datanode_deleted(callback=cb_for_state)
        mck.assert_called_once_with(callback=cb_for_state,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.DELETION,
                                    filter=ANY,
                                    broadcast=True)
