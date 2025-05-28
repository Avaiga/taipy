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

from taipy import DataNode, Gui
from taipy.core.config import DataNodeConfig
from taipy.core.notification import Event, EventEntityType, EventOperation
from taipy.event.event_processor import EventProcessor


def cb_0(event: Event, datanode: DataNode):
    ...


def cb_1(event: Event, datanode: DataNode, extra:str):
    ...


def cb_for_state(state, event: Event, datanode: DataNode):
    ...


def test_on_datanode_created(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_created(callback=cb_0)
        # test the on_datanode_created method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.CREATION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.CREATION, entity_id=data_node.id)
        assert actual_filter is not None
        with (mock.patch("taipy.get") as mck_get):
            mck_get.return_value = data_node
            filter_value = actual_filter(event)
            mck_get.assert_called_once_with(data_node.id)
            assert filter_value is True  # No config provided, so the datanode passes the filter
            assert event.metadata["predefined_args"] == [data_node]


def test_on_datanode_created_multiple_configs(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_created(callback=cb_0,
                                     datanode_config=[DataNodeConfig("dn0"), "dn1", DataNodeConfig("dn2"), "data_node"])
        # test the on_datanode_created method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.CREATION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.CREATION, entity_id=data_node.id)
        assert actual_filter is not None
        with (mock.patch("taipy.get") as mck_get):
            mck_get.return_value = data_node
            filter_value = actual_filter(event)
            mck_get.assert_called_once_with(data_node.id)
            assert filter_value is True  # The datanode is from config 'data_node', so the datanode passes the filter
            assert event.metadata["predefined_args"] == [data_node]


def test_on_datanode_created_multiple_configs_no_matching(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_created(callback=cb_0,
                                     datanode_config=[DataNodeConfig("dn0"), "dn1"])
        # test the on_datanode_created method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.CREATION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.CREATION,
                      entity_id=data_node.id)
        assert actual_filter is not None
        with (mock.patch("taipy.get") as mck_get):
            mck_get.return_value = data_node
            f_val = actual_filter(event)
            mck_get.assert_called_once_with(data_node.id)
            assert not f_val  # DataNode is not from any of the provided configs, so it should not pass the filter
            assert event.metadata.get("predefined_args") is None


def test_on_datanode_created_with_args_and_matching_config(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_created(callback=cb_1, callback_args=["foo"], datanode_config="data_node")
        # test the on_datanode_created method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_1,
                                    callback_args=["foo"],
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.CREATION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.CREATION, entity_id=data_node.id)
        with (mock.patch("taipy.get") as mck_get):
            mck_get.return_value = data_node
            filter_value = actual_filter(event)
            mck_get.assert_called_once_with(data_node.id)
            assert filter_value is True # datanode is from config 'data_node', so the datanode passes the filter
            assert event.metadata.get("predefined_args") == [data_node]


def test_on_datanode_created_with_args_and_not_matching_config(data_node):
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_datanode_created(callback=cb_1, callback_args=["foo"], datanode_config="WRONG_CFG")
        # test the on_datanode_created method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_1,
                                    callback_args=["foo"],
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.CREATION,
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None
        event = Event(entity_type=EventEntityType.DATA_NODE, operation=EventOperation.CREATION, entity_id=data_node.id)
        with (mock.patch("taipy.get") as mck_get):
            mck_get.return_value = data_node
            filter_value = actual_filter(event)
            mck_get.assert_called_once_with(data_node.id)
            assert filter_value is False  # datanode is not from WRONG_CFG, so it should not pass the filter
            assert event.metadata.get("predefined_args") is None # No need to cache the datanode in the metadata


def test_on_datanode_created_with_broadcast():
    consumer = EventProcessor(Gui())
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.broadcast_on_datanode_created(callback=cb_for_state)
        mck.assert_called_once_with(callback=cb_for_state,
                                    callback_args=None,
                                    entity_type=EventEntityType.DATA_NODE,
                                    operation=EventOperation.CREATION,
                                    filter=ANY,
                                    broadcast=True)

