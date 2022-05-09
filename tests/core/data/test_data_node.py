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

from datetime import datetime, timedelta
from time import sleep
from unittest import mock

import pytest

import taipy.core as tp
from taipy.core import Config
from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.common.scope import Scope
from taipy.core.data._data_manager import _DataManager
from taipy.core.data._filter import _FilterDataNode
from taipy.core.data.data_node import DataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.exceptions.exceptions import InvalidConfigurationId, NoData


class FakeDataNode(InMemoryDataNode):
    read_has_been_called = 0
    write_has_been_called = 0

    def __init__(self, config_id, **kwargs):
        super().__init__(config_id, Scope.PIPELINE, **kwargs)

    def _read(self, query=None):
        self.read_has_been_called += 1

    def _write(self, data):
        self.write_has_been_called += 1

    write = DataNode.write  # Make sure that the writing behavior comes from DataNode


class FakeDataframeDataNode(DataNode):
    COLUMN_NAME_1 = "a"
    COLUMN_NAME_2 = "b"

    def __init__(self, config_id, default_data_frame, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = default_data_frame

    def _read(self):
        return self.data


class FakeListDataNode(DataNode):
    class Row:
        def __init__(self, value):
            self.value = value

    def __init__(self, config_id, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = [self.Row(i) for i in range(10)]

    def _read(self):
        return self.data


def funct_a_b(input: str):
    print("task_a_b")
    return "B"


def funct_b_c(input: str):
    print("task_b_c")
    return "C"


def funct_b_d(input: str):
    print("task_b_d")
    return "D"


class TestDataNode:
    def test_create_with_default_values(self):
        dn = DataNode("foo_bar")
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.name == dn.id
        assert dn.parent_id is None
        assert dn.last_edition_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert len(dn.properties) == 0

    def test_create(self):
        a_date = datetime.now()
        dn = DataNode(
            "foo_bar",
            Scope.SCENARIO,
            DataNodeId("an_id"),
            "a name",
            "a_scenario_id",
            a_date,
            [JobId("a_job_id")],
            edit_in_progress=False,
            prop="erty",
        )
        assert dn.config_id == "foo_bar"
        assert dn.scope == Scope.SCENARIO
        assert dn.id == "an_id"
        assert dn.name == "a name"
        assert dn.parent_id == "a_scenario_id"
        assert dn.last_edition_date == a_date
        assert dn.job_ids == ["a_job_id"]
        assert dn.is_ready_for_reading
        assert len(dn.properties) == 1
        assert dn.properties["prop"] == "erty"

        with pytest.raises(InvalidConfigurationId):
            DataNode("foo bar")

    def test_read_write(self):
        dn = FakeDataNode("foo_bar")
        with pytest.raises(NoData):
            assert dn.read() is None
            dn.read_or_raise()
        assert dn.write_has_been_called == 0
        assert dn.read_has_been_called == 0
        assert not dn.is_ready_for_reading
        assert dn.last_edition_date is None
        assert dn.job_ids == []

        dn.write("Any data")
        assert dn.write_has_been_called == 1
        assert dn.read_has_been_called == 0
        assert dn.last_edition_date is not None
        first_edition = dn.last_edition_date
        assert dn.is_ready_for_reading
        assert dn.job_ids == []
        sleep(0.1)

        dn.write("Any other data", job_id := JobId("a_job_id"))
        assert dn.write_has_been_called == 2
        assert dn.read_has_been_called == 0
        second_edition = dn.last_edition_date
        assert first_edition < second_edition
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

        dn.read()
        assert dn.write_has_been_called == 2
        assert dn.read_has_been_called == 1
        second_edition = dn.last_edition_date
        assert first_edition < second_edition
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

    def test_ready_for_reading(self):
        dn = InMemoryDataNode("foo_bar", Scope.CYCLE)
        assert dn.last_edition_date is None
        assert not dn.is_ready_for_reading
        assert dn.job_ids == []

        dn.lock_edition()
        assert dn.last_edition_date is None
        assert not dn.is_ready_for_reading
        assert dn.job_ids == []

        dn.unlock_edition(a_date := datetime.now(), job_id := JobId("a_job_id"))
        assert dn.last_edition_date == a_date
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

        dn.lock_edition()
        assert dn.last_edition_date == a_date
        assert not dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

        dn.unlock_edition(b_date := datetime.now())
        assert dn.last_edition_date == b_date
        assert dn.is_ready_for_reading
        assert dn.job_ids == [job_id]

    def test_is_in_cache_no_validity_period_cacheable_false(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("id"), "name", "parent_id")
        assert not dn._is_in_cache

        # test has been writen
        dn.write("My data")
        assert dn._is_in_cache is False

    def test_is_in_cache_no_validity_period_cacheable_true(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("id"), "name", None, properties={"cacheable": True})
        assert dn._is_in_cache is False

        # test has been writen
        dn.write("My data")
        assert dn._is_in_cache is True

    def test_is_in_cache_with_30_min_validity_period_cacheable_false(self):
        # Test Never been writen
        dn = InMemoryDataNode(
            "foo", Scope.PIPELINE, DataNodeId("id"), "name", "parent_id", validity_period=timedelta(minutes=30)
        )
        assert dn._is_in_cache is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn._is_in_cache is False

        # Has been writen more than 30 minutes ago
        dn._last_edition_date = datetime.now() + timedelta(days=-1)
        _DataManager._set(dn)
        assert dn._is_in_cache is False

    def test_is_in_cache_with_30_min_validity_period_cacheable_true(self):
        # Test Never been writen
        dn = InMemoryDataNode(
            "foo", Scope.PIPELINE, properties={"cacheable": True}, validity_period=timedelta(minutes=30)
        )
        assert dn._is_in_cache is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn._is_in_cache is True

        # Has been writen more than 30 minutes ago
        dn._last_edit_date = datetime.now() - timedelta(days=1)
        _DataManager()._set(dn)
        assert dn._is_in_cache is False

    def test_is_in_cache_with_5_days_validity_period_cacheable_true(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.PIPELINE, properties={"cacheable": True}, validity_period=timedelta(days=5))
        assert dn._is_in_cache is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn._is_in_cache is True

        # Has been writen more than 30 minutes ago
        dn._last_edit_date = datetime.now() - timedelta(days=6)
        _DataManager()._set(dn)
        assert dn._is_in_cache is False

    def test_do_not_recompute_data_node_in_cache_but_continue_pipeline_execution(self):
        a = Config.configure_data_node("A", "pickle", default_data="A")
        b = Config.configure_data_node("B", "pickle", cacheable=True)
        c = Config.configure_data_node("C", "pickle")
        d = Config.configure_data_node("D", "pickle")

        task_a_b = Config.configure_task("task_a_b", funct_a_b, input=a, output=b)
        task_b_c = Config.configure_task("task_b_c", funct_b_c, input=b, output=c)
        task_b_d = Config.configure_task("task_b_d", funct_b_d, input=b, output=d)
        pipeline_c = Config.configure_pipeline("pipeline_c", [task_a_b, task_b_c])
        pipeline_d = Config.configure_pipeline("pipeline_d", [task_a_b, task_b_d])
        scenario_cfg = Config.configure_scenario("scenario", [pipeline_c, pipeline_d])

        scenario = tp.create_scenario(scenario_cfg)
        scenario.submit()
        assert scenario.A.read() == "A"
        assert scenario.B.read() == "B"
        assert scenario.C.read() == "C"
        assert scenario.D.read() == "D"

        assert len(tp.get_jobs()) == 4
        jobs_and_status = [(job.task.config_id, job.status) for job in tp.get_jobs()]
        assert ("task_a_b", tp.Status.COMPLETED) in jobs_and_status
        assert ("task_a_b", tp.Status.SKIPPED) in jobs_and_status
        assert ("task_b_c", tp.Status.COMPLETED) in jobs_and_status
        assert ("task_b_d", tp.Status.COMPLETED) in jobs_and_status

    def test_pandas_filter(self, default_data_frame):
        df_dn = FakeDataframeDataNode("fake_dataframe_dn", default_data_frame)
        COLUMN_NAME_1 = "a"
        COLUMN_NAME_2 = "b"
        assert isinstance(df_dn[COLUMN_NAME_1], _FilterDataNode)
        assert isinstance(df_dn[[COLUMN_NAME_1, COLUMN_NAME_2]], _FilterDataNode)

    def test_filter(self, default_data_frame):
        dn = FakeDataNode("fake_dn")
        dn.write("Any data")

        assert NotImplemented == dn.filter((("any", 0, Operator.EQUAL)), JoinOperator.OR)
        assert NotImplemented == dn.filter((("any", 0, Operator.NOT_EQUAL)), JoinOperator.OR)
        assert NotImplemented == dn.filter((("any", 0, Operator.LESS_THAN)), JoinOperator.AND)
        assert NotImplemented == dn.filter((("any", 0, Operator.LESS_OR_EQUAL)), JoinOperator.AND)
        assert NotImplemented == dn.filter((("any", 0, Operator.GREATER_THAN)))
        assert NotImplemented == dn.filter((("any", 0, Operator.GREATER_OR_EQUAL)))

        df_dn = FakeDataframeDataNode("fake_dataframe_dn", default_data_frame)

        COLUMN_NAME_1 = "a"
        COLUMN_NAME_2 = "b"
        assert len(df_dn.filter((COLUMN_NAME_1, 1, Operator.EQUAL))) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] == 1]
        )
        assert len(df_dn.filter((COLUMN_NAME_1, 1, Operator.NOT_EQUAL))) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] != 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] == 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.NOT_EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] != 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.LESS_THAN)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] < 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.LESS_OR_EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] <= 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.GREATER_THAN)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] > 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, 1, Operator.GREATER_OR_EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] >= 1]
        )
        assert len(df_dn.filter([(COLUMN_NAME_1, -1000, Operator.LESS_OR_EQUAL)])) == 0
        assert len(df_dn.filter([(COLUMN_NAME_1, 1000, Operator.GREATER_OR_EQUAL)])) == 0
        assert len(df_dn.filter([(COLUMN_NAME_1, 4, Operator.EQUAL), (COLUMN_NAME_1, 5, Operator.EQUAL)])) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] == 4) & (default_data_frame[COLUMN_NAME_1] == 5)]
        )
        assert len(
            df_dn.filter([(COLUMN_NAME_1, 4, Operator.EQUAL), (COLUMN_NAME_2, 5, Operator.EQUAL)], JoinOperator.OR)
        ) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] == 4) | (default_data_frame[COLUMN_NAME_2] == 5)]
        )
        assert len(
            df_dn.filter(
                [(COLUMN_NAME_1, 1, Operator.GREATER_THAN), (COLUMN_NAME_2, 3, Operator.GREATER_THAN)], JoinOperator.AND
            )
        ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 1) & (default_data_frame[COLUMN_NAME_2] > 3)])
        assert len(
            df_dn.filter(
                [(COLUMN_NAME_1, 2, Operator.GREATER_THAN), (COLUMN_NAME_1, 3, Operator.GREATER_THAN)], JoinOperator.OR
            )
        ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 2) | (default_data_frame[COLUMN_NAME_1] > 3)])
        assert len(
            df_dn.filter(
                [(COLUMN_NAME_1, 10, Operator.GREATER_THAN), (COLUMN_NAME_1, -10, Operator.LESS_THAN)], JoinOperator.AND
            )
        ) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] > 10) | (default_data_frame[COLUMN_NAME_1] < -10)]
        )
        assert len(
            df_dn.filter(
                [(COLUMN_NAME_1, 10, Operator.GREATER_THAN), (COLUMN_NAME_1, -10, Operator.LESS_THAN)], JoinOperator.OR
            )
        ) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] > 10) | (default_data_frame[COLUMN_NAME_1] < -10)]
        )
        list_dn = FakeListDataNode("fake_list_dn")

        KEY_NAME = "value"

        assert len(list_dn.filter((KEY_NAME, 4, Operator.EQUAL))) == 1
        assert len(list_dn.filter((KEY_NAME, 4, Operator.NOT_EQUAL))) == 9
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL)])) == 1
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.NOT_EQUAL)])) == 9
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.LESS_THAN)])) == 4
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.LESS_OR_EQUAL)])) == 5
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.GREATER_THAN)])) == 5
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.GREATER_OR_EQUAL)])) == 6
        assert len(list_dn.filter([(KEY_NAME, -1000, Operator.LESS_OR_EQUAL)])) == 0
        assert len(list_dn.filter([(KEY_NAME, 1000, Operator.GREATER_OR_EQUAL)])) == 0

        assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 5, Operator.EQUAL)])) == 0
        assert len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 5, Operator.EQUAL)], JoinOperator.OR)) == 2
        assert (
            len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 11, Operator.EQUAL)], JoinOperator.AND)) == 0
        )
        assert (
            len(list_dn.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 11, Operator.EQUAL)], JoinOperator.OR)) == 1
        )

        assert (
            len(list_dn.filter([(KEY_NAME, -10, Operator.LESS_OR_EQUAL), (KEY_NAME, 11, Operator.GREATER_OR_EQUAL)]))
            == 0
        )
        assert (
            len(
                list_dn.filter(
                    [
                        (KEY_NAME, 4, Operator.GREATER_OR_EQUAL),
                        (KEY_NAME, 6, Operator.GREATER_OR_EQUAL),
                    ],
                    JoinOperator.AND,
                )
            )
            == 4
        )
        assert (
            len(
                list_dn.filter(
                    [
                        (KEY_NAME, 4, Operator.GREATER_OR_EQUAL),
                        (KEY_NAME, 6, Operator.GREATER_OR_EQUAL),
                        (KEY_NAME, 11, Operator.EQUAL),
                    ],
                    JoinOperator.AND,
                )
            )
            == 0
        )
        assert (
            len(
                list_dn.filter(
                    [
                        (KEY_NAME, 4, Operator.GREATER_OR_EQUAL),
                        (KEY_NAME, 6, Operator.GREATER_OR_EQUAL),
                        (KEY_NAME, 11, Operator.EQUAL),
                    ],
                    JoinOperator.OR,
                )
            )
            == 6
        )

    def test_data_node_update_after_writing(self):
        dn = FakeDataNode("foo")

        _DataManager._set(dn)
        assert not _DataManager._get(dn.id).is_ready_for_reading
        dn.write("Any data")

        assert dn.is_ready_for_reading
        assert _DataManager._get(dn.id).is_ready_for_reading

    def test_expiration_date_raise_if_never_write(self):
        dn = FakeDataNode("foo")

        with pytest.raises(NoData):
            dn.expiration_date

    def test_validity_null_if_never_write(self):
        dn = FakeDataNode("foo")

        assert dn.validity_period is None

    def test_auto_set_and_reload(self, current_datetime):
        dn_1 = InMemoryDataNode(
            "foo",
            scope=Scope.SCENARIO,
            id=DataNodeId("an_id"),
            name="foo",
            parent_id=None,
            last_edit_date=current_datetime,
            job_ids=[JobId("a_job_id")],
            edit_in_progress=False,
            validity_period=None,
        )

        dm = _DataManager()
        dm._set(dn_1)

        dn_2 = dm._get(dn_1)

        assert dn_1.scope == Scope.SCENARIO
        dn_1.scope = Scope.PIPELINE
        assert dn_1.scope == Scope.PIPELINE
        assert dn_2.scope == Scope.PIPELINE

        new_datetime = current_datetime + timedelta(1)

        assert dn_1.last_edition_date == current_datetime
        dn_1.last_edition_date = new_datetime
        assert dn_1.last_edition_date == new_datetime
        assert dn_2.last_edition_date == new_datetime

        assert dn_1.name == "foo"
        dn_1.name = "def"
        assert dn_1.name == "def"
        assert dn_2.name == "def"

        assert not dn_1.edition_in_progress
        dn_1.edition_in_progress = True
        assert dn_1.edition_in_progress
        assert dn_2.edition_in_progress
        dn_1.unlock_edition()
        assert not dn_1.edition_in_progress
        assert not dn_2.edition_in_progress
        dn_1.lock_edition()
        assert dn_1.edition_in_progress
        assert dn_2.edition_in_progress

        time_period = timedelta(1)

        assert dn_1.validity_period is None
        dn_1.validity_period = time_period
        assert dn_1.validity_period == time_period
        assert dn_2.validity_period == time_period

        assert dn_1.properties == {}
        dn_1.properties["qux"] = 5
        assert dn_1.properties["qux"] == 5
        assert dn_2.properties["qux"] == 5

        dn_1.last_edition_date = new_datetime

        assert len(dn_1.job_ids) == 1
        dn_1.job_ids.append("a_job_id_2")
        assert len(dn_1.job_ids) == 2
        assert len(dn_2.job_ids) == 2

        dn_1.job_ids = []
        assert len(dn_1.job_ids) == 0
        assert len(dn_2.job_ids) == 0

        with dn_1 as dn:
            assert dn.config_id == "foo"
            assert dn.parent_id is None
            assert dn.scope == Scope.PIPELINE
            assert dn.last_edition_date == new_datetime
            assert dn.name == "def"
            assert dn.edition_in_progress
            assert dn.validity_period == time_period
            assert len(dn.job_ids) == 0
            assert dn._is_in_context

            new_datetime_2 = new_datetime + timedelta(1)

            dn.scope = Scope.CYCLE
            dn.last_edition_date = new_datetime_2
            dn.name = "abc"
            dn.edition_in_progress = False
            dn.validity_period = None
            dn.job_ids = ["a_job_id"]

            assert dn.config_id == "foo"
            assert dn.parent_id is None
            assert dn.scope == Scope.PIPELINE
            assert dn.last_edition_date == new_datetime
            assert dn.name == "def"
            assert dn.edition_in_progress
            assert dn.validity_period == time_period
            assert len(dn.job_ids) == 0

        assert dn_1.config_id == "foo"
        assert dn_1.parent_id is None
        assert dn_1.scope == Scope.CYCLE
        assert dn_1.last_edition_date == new_datetime_2
        assert dn_1.name == "abc"
        assert not dn_1.edition_in_progress
        assert dn_1.validity_period is None
        assert not dn_1._is_in_context
        assert len(dn_1.job_ids) == 1

    def test_unlock_edition_deprecated(self):
        dn = FakeDataNode("foo")

        with pytest.warns(DeprecationWarning):
            with mock.patch("taipy.core.data.data_node.DataNode.unlock_edit") as unlock_edit:
                dn.unlock_edition(d := datetime.now(), None)
                unlock_edit.assert_called_once_with(d, None)

    def test_lock_edition_deprecated(self):
        dn = FakeDataNode("foo")

        with pytest.warns(DeprecationWarning):
            with mock.patch("taipy.core.data.data_node.DataNode.lock_edit") as lock_edit:
                dn.lock_edition()
                lock_edit.assert_called_once()

    def test_edition_in_progress_deprecated(self):
        dn = FakeDataNode("foo")

        with pytest.warns(DeprecationWarning):
            dn.edition_in_progress

        assert dn.edit_in_progress == dn.edition_in_progress
        dn.edition_in_progress = True
        assert dn.edit_in_progress == dn.edition_in_progress

    def test_last_edition_date_deprecated(self):
        dn = FakeDataNode("foo")

        with pytest.warns(DeprecationWarning):
            dn.last_edition_date

        assert dn.last_edit_date == dn.last_edition_date
        dn.last_edition_date = datetime.now()
        assert dn.last_edit_date == dn.last_edition_date
