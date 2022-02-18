from datetime import datetime, timedelta
from time import sleep

import pytest

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.data.data_manager import DataManager
from taipy.core.data.data_node import DataNode
from taipy.core.data.filter import FilterDataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.data.scope import Scope
from taipy.core.exceptions.data_node import NoData


class FakeDataNode(InMemoryDataNode):
    read_has_been_called = 0
    write_has_been_called = 0

    def __init__(self, config_name, **kwargs):
        super().__init__(config_name, Scope.PIPELINE, **kwargs)

    def _read(self, query=None):
        self.read_has_been_called += 1

    def _write(self, data):
        self.write_has_been_called += 1

    write = DataNode.write  # Make sure that the writing behavior comes from DataNode


class FakeDataframeDataNode(DataNode):
    COLUMN_NAME_1 = "a"
    COLUMN_NAME_2 = "b"

    def __init__(self, config_name, default_data_frame, **kwargs):
        super().__init__(config_name, **kwargs)
        self.data = default_data_frame

    def _read(self):
        return self.data


class FakeListDataNode(DataNode):
    class Row:
        def __init__(self, value):
            self.value = value

    def __init__(self, config_name, **kwargs):
        super().__init__(config_name, **kwargs)
        self.data = [self.Row(i) for i in range(10)]

    def _read(self):
        return self.data


class TestDataNode:
    def test_create_with_default_values(self):
        dn = DataNode("fOo BAr")
        assert dn.config_name == "foo_bar"
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
            "fOo BAr é@",
            Scope.SCENARIO,
            DataNodeId("an_id"),
            "a name",
            "a_scenario_id",
            a_date,
            [JobId("a_job_id")],
            edition_in_progress=False,
            prop="erty",
        )
        assert dn.config_name == "foo_bar_e-"
        assert dn.scope == Scope.SCENARIO
        assert dn.id == "an_id"
        assert dn.name == "a name"
        assert dn.parent_id == "a_scenario_id"
        assert dn.last_edition_date == a_date
        assert dn.job_ids == ["a_job_id"]
        assert dn.is_ready_for_reading
        assert len(dn.properties) == 1
        assert dn.properties["prop"] == "erty"

    def test_read_write(self):
        dn = FakeDataNode("fOo BAr")
        with pytest.raises(NoData):
            dn.read()
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
        dn = DataNode("fOo BAr")
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
        assert not dn.is_in_cache

        # test has been writen
        dn.write("My data")
        assert dn.is_in_cache is False

    def test_is_in_cache_no_validity_period_cacheable_true(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("id"), "name", None, properties={"cacheable": True})
        assert dn.is_in_cache is False

        # test has been writen
        dn.write("My data")
        assert dn.is_in_cache is True

    def test_is_in_cache_with_30_min_validity_period_cacheable_false(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("id"), "name", "parent_id", validity_minutes=30)
        assert dn.is_in_cache is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn.is_in_cache is False

        # Has been writen more than 30 minutes ago
        dn._last_edition_date = datetime.now() + timedelta(days=-1)
        DataManager.set(dn)
        assert dn.is_in_cache is False

    def test_is_in_cache_with_30_min_validity_period_cacheable_true(self):
        # Test Never been writen
        dn = InMemoryDataNode("foo", Scope.PIPELINE, properties={"cacheable": True}, validity_minutes=30)
        assert dn.is_in_cache is False

        # Has been writen less than 30 minutes ago
        dn.write("My data")
        assert dn.is_in_cache is True

        # Has been writen more than 30 minutes ago
        dn._last_edition_date = datetime.now() + timedelta(days=-1)
        DataManager().set(dn)
        assert dn.is_in_cache is False

    def test_pandas_filter(self, default_data_frame):
        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)
        COLUMN_NAME_1 = "a"
        COLUMN_NAME_2 = "b"
        assert isinstance(df_dn[COLUMN_NAME_1], FilterDataNode)
        assert isinstance(df_dn[[COLUMN_NAME_1, COLUMN_NAME_2]], FilterDataNode)

    def test_filter(self, default_data_frame):
        dn = FakeDataNode("fake dn")
        dn.write("Any data")

        assert NotImplemented == dn.filter((("any", 0, Operator.EQUAL)), JoinOperator.OR)
        assert NotImplemented == dn.filter((("any", 0, Operator.NOT_EQUAL)), JoinOperator.OR)
        assert NotImplemented == dn.filter((("any", 0, Operator.LESS_THAN)), JoinOperator.AND)
        assert NotImplemented == dn.filter((("any", 0, Operator.LESS_OR_EQUAL)), JoinOperator.AND)
        assert NotImplemented == dn.filter((("any", 0, Operator.GREATER_THAN)))
        assert NotImplemented == dn.filter((("any", 0, Operator.GREATER_OR_EQUAL)))

        df_dn = FakeDataframeDataNode("fake dataframe dn", default_data_frame)

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
        list_dn = FakeListDataNode("fake list dn")

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

        DataManager.set(dn)
        assert not DataManager.get(dn.id).is_ready_for_reading
        dn.write("Any data")

        assert dn.is_ready_for_reading
        assert DataManager.get(dn.id).is_ready_for_reading

    def test_auto_reload(self):
        dm = DataManager()
        dn = FakeDataNode("foo")

        dm.set(dn)
        dn_bis = dm.get(dn)

        dn._name = "new_name"
        dn._validity_days = 3
        dn._validity_hours = 2
        dn._validity_minutes = 1
        dn.write("Any data")

        assert dn.last_edition_date is not None
        assert dn.last_edition_date == dn_bis.last_edition_date
        assert dn.name == dn_bis.name == "new_name"
        assert dn._validity_days != dn_bis._validity_days
        assert dn._validity_hours != dn_bis._validity_hours
        assert dn._validity_minutes != dn_bis._validity_minutes
        assert dn.write_has_been_called == 1
        assert dn.validity() == dn_bis.validity() == 3 * 24 * 60 + 2 * 60 + 1
        assert dn.expiration_date() == dn_bis.expiration_date()
        assert dn.expiration_date() > dn.last_edition_date

        assert dn.job_ids == dn_bis.job_ids

        dn.lock_edition()
        dm.set(dn)
        assert dn.edition_in_progress == dn_bis.edition_in_progress is True

        dn.unlock_edition()
        dm.set(dn)
        assert dn.edition_in_progress == dn_bis.edition_in_progress is False

        dn.properties["qux"] = 5
        same_dn = dm.get(dn.id)
        assert dn.properties["qux"] == 5
        assert same_dn.properties["qux"] == 5

    def test_expiration_date_raise_if_never_write(self):
        dn = FakeDataNode("foo")

        with pytest.raises(NoData):
            dn.expiration_date()

    def test_validity_null_if_never_write(self):
        dn = FakeDataNode("foo")

        assert dn.validity() == 0
