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

from taipy import Gui, Scenario, Submission, SubmissionStatus
from taipy.core.notification import Event, EventEntityType, EventOperation
from taipy.event.event_processor import EventProcessor


def cb_0(event: Event, submittable: Scenario, submission: Submission):
    ...


def cb_1(event: Event, submittable: Scenario, submission: Submission, extra:str):
    ...


def cb_for_state(state, event: Event, submittable: Scenario, submission: Submission):
    ...


def test_on_scenario_submission_finished(scenario, submission):
    submission._entity_id = scenario.id
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_0)
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None
        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                        attribute_value=SubmissionStatus.COMPLETED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_has_calls(calls=[mock.call(submission.id), mock.call(scenario.id)], any_order=False)
            assert filter_value is True  # No config provided, so the event passes the filter
            assert event.metadata["predefined_args"] == [scenario, submission]

        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                        attribute_value=SubmissionStatus.FAILED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_has_calls(calls=[mock.call(submission.id), mock.call(scenario.id)], any_order=False)
            assert filter_value is True  # No config provided, so the event passes the filter
            assert event.metadata["predefined_args"] == [scenario, submission]

        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                        attribute_value=SubmissionStatus.CANCELED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_has_calls(calls=[mock.call(submission.id), mock.call(scenario.id)], any_order=False)
            assert filter_value is True  # No config provided, so the event passes the filter
            assert event.metadata["predefined_args"] == [scenario, submission]


def test_filter_false__wrong_status(scenario, submission):
    submission._entity_id = scenario.id
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_0)
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None

        # No status value
        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                      )
        filter_value = actual_filter(event)
        assert filter_value is False  # no status value
        assert event.metadata.get("predefined_args") is None

        # wrong status
        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                      attribute_value=SubmissionStatus.BLOCKED,
                      )
        filter_value = actual_filter(event)
        assert filter_value is False  # status is not finished
        assert event.metadata.get("predefined_args") is None


def test_filter_false__config_ids_and_sequence(scenario, sequence, submission):
    submission._entity_id = sequence.id
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_0, config_ids=scenario.config_id)
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None

        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                      attribute_value=SubmissionStatus.COMPLETED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_called_once_with(submission.id)
            assert filter_value is False  # Sequence submission do not have config so the event does not pass the filter
            assert event.metadata.get("predefined_args") is None


def test_filter_false__not_matching_config_ids(scenario, submission):
    submission._entity_id = scenario.id
    submission._entity_config_id = scenario.config_id
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_0, config_ids=["NOT_MATCHING_CONFIG_ID"])
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None

        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                      attribute_value=SubmissionStatus.COMPLETED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_called_once_with(submission.id)
            # Submission config id is not in the provided list so the event does not pass the filter
            assert filter_value is False
            assert event.metadata.get("predefined_args") is None


def test_filter_true__with_config(scenario, submission):
    submission._entity_id = scenario.id
    submission._entity_config_id = scenario.config_id
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_0, config_ids=["scenario_cfg", scenario.config_id])
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None

        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                      attribute_value=SubmissionStatus.COMPLETED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_has_calls([mock.call(submission.id), mock.call(scenario.id)])
            assert filter_value is True
            assert event.metadata.get("predefined_args") == [scenario, submission]


def test_filter_true__without_config(scenario, submission):
    submission._entity_id = scenario.id
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_0)
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_0,
                                    callback_args=None,
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)

        # check the filter method is correct
        actual_filter = mck.call_args.kwargs["filter"]
        assert actual_filter is not None

        event = Event(entity_type=EventEntityType.SUBMISSION,
                      operation=EventOperation.UPDATE,
                      entity_id=submission.id,
                      attribute_name="submission_status",
                      attribute_value=SubmissionStatus.COMPLETED,
                      )
        with (mock.patch("taipy.get") as mck_get):
            mck_get.side_effect = [submission, scenario]
            filter_value = actual_filter(event)
            mck_get.assert_has_calls([mock.call(submission.id), mock.call(scenario.id)])
            assert filter_value is True
            assert event.metadata.get("predefined_args") == [scenario, submission]


def test_on_scenario_submission_finished_with_args():
    consumer = EventProcessor()
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.on_submission_finished(callback=cb_1, callback_args=["extra"])
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_1,
                                    callback_args=["extra"],
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=False)


def test_on_scenario_submission_finished_with_args_and_state():
    consumer = EventProcessor(gui=Gui())
    with mock.patch("taipy.event.event_processor.EventProcessor._EventProcessor__on_event") as mck:
        consumer.broadcast_on_submission_finished(callback=cb_for_state, callback_args=["extra"])
        # test the on_submission_finished method delegates to on_event with the correct parameters
        mck.assert_called_once_with(callback=cb_for_state,
                                    callback_args=["extra"],
                                    entity_type=EventEntityType.SUBMISSION,
                                    operation=EventOperation.UPDATE,
                                    attribute_name="submission_status",
                                    filter=ANY,
                                    broadcast=True)
