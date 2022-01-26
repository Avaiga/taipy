from datetime import datetime, timedelta
from time import sleep

import pytest

from taipy.common.alias import DataNodeId, JobId
from taipy.data import DataNode, InMemoryDataNode, Scope
from taipy.data.filter_data_node import FilterDataNode
from taipy.data.manager import DataManager
from taipy.data.operator import JoinOperator, Operator
from taipy.exceptions.data_node import NoData


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
        ds = DataNode("fOo BAr")
        assert ds.config_name == "foo_bar"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.name == ds.id
        assert ds.parent_id is None
        assert ds.last_edition_date is None
        assert ds.job_ids == []
        assert not ds.is_ready_for_reading
        assert len(ds.properties) == 0

    def test_create(self):
        a_date = datetime.now()
        ds = DataNode(
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
        assert ds.config_name == "foo_bar_e-"
        assert ds.scope == Scope.SCENARIO
        assert ds.id == "an_id"
        assert ds.name == "a name"
        assert ds.parent_id == "a_scenario_id"
        assert ds.last_edition_date == a_date
        assert ds.job_ids == ["a_job_id"]
        assert ds.is_ready_for_reading
        assert len(ds.properties) == 1
        assert ds.properties["prop"] == "erty"

    def test_read_write(self):
        ds = FakeDataNode("fOo BAr")
        with pytest.raises(NoData):
            ds.read()
        assert ds.write_has_been_called == 0
        assert ds.read_has_been_called == 0
        assert not ds.is_ready_for_reading
        assert ds.last_edition_date is None
        assert ds.job_ids == []

        ds.write("Any data")
        assert ds.write_has_been_called == 1
        assert ds.read_has_been_called == 0
        assert ds.last_edition_date is not None
        first_edition = ds.last_edition_date
        assert ds.is_ready_for_reading
        assert ds.job_ids == []
        sleep(0.1)

        ds.write("Any other data", job_id := JobId("a_job_id"))
        assert ds.write_has_been_called == 2
        assert ds.read_has_been_called == 0
        second_edition = ds.last_edition_date
        assert first_edition < second_edition
        assert ds.is_ready_for_reading
        assert ds.job_ids == [job_id]

        ds.read()
        assert ds.write_has_been_called == 2
        assert ds.read_has_been_called == 1
        second_edition = ds.last_edition_date
        assert first_edition < second_edition
        assert ds.is_ready_for_reading
        assert ds.job_ids == [job_id]

    def test_ready_for_reading(self):
        ds = DataNode("fOo BAr")
        assert ds.last_edition_date is None
        assert not ds.is_ready_for_reading
        assert ds.job_ids == []

        ds.lock_edition()
        assert ds.last_edition_date is None
        assert not ds.is_ready_for_reading
        assert ds.job_ids == []

        ds.unlock_edition(a_date := datetime.now(), job_id := JobId("a_job_id"))
        assert ds.last_edition_date == a_date
        assert ds.is_ready_for_reading
        assert ds.job_ids == [job_id]

        ds.lock_edition()
        assert ds.last_edition_date == a_date
        assert not ds.is_ready_for_reading
        assert ds.job_ids == [job_id]

        ds.unlock_edition(b_date := datetime.now())
        assert ds.last_edition_date == b_date
        assert ds.is_ready_for_reading
        assert ds.job_ids == [job_id]

    def test_is_up_to_date_no_validity_period(self):
        # Test Never been writen
        ds = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("id"), "name", "parent_id")
        assert ds.is_up_to_date is False

        # test has been writen
        ds.write("My data")
        assert ds.is_up_to_date is True

    def test_is_up_to_date_with_30_min_validity_period(self):
        # Test Never been writen
        ds = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("id"), "name", "parent_id", validity_minutes=30)
        assert ds.is_up_to_date is False

        # Has been writen less than 30 minutes ago
        ds.write("My data")
        assert ds.is_up_to_date is True

        # Has been writen more than 30 minutes ago
        ds.last_edition_date = datetime.now() + timedelta(days=-1)
        assert ds.is_up_to_date is False

    def test_pandas_filter(self, default_data_frame):
        df_ds = FakeDataframeDataNode("fake dataframe ds", default_data_frame)
        COLUMN_NAME_1 = "a"
        COLUMN_NAME_2 = "b"
        assert isinstance(df_ds[COLUMN_NAME_1], FilterDataNode)
        assert isinstance(df_ds[[COLUMN_NAME_1, COLUMN_NAME_2]], FilterDataNode)

    def test_filter(self, default_data_frame):
        ds = FakeDataNode("fake ds")
        ds.write("Any data")

        assert NotImplemented == ds.filter((("any", 0, Operator.EQUAL)), JoinOperator.OR)
        assert NotImplemented == ds.filter((("any", 0, Operator.NOT_EQUAL)), JoinOperator.OR)
        assert NotImplemented == ds.filter((("any", 0, Operator.LESS_THAN)), JoinOperator.AND)
        assert NotImplemented == ds.filter((("any", 0, Operator.LESS_OR_EQUAL)), JoinOperator.AND)
        assert NotImplemented == ds.filter((("any", 0, Operator.GREATER_THAN)))
        assert NotImplemented == ds.filter((("any", 0, Operator.GREATER_OR_EQUAL)))

        df_ds = FakeDataframeDataNode("fake dataframe ds", default_data_frame)

        COLUMN_NAME_1 = "a"
        COLUMN_NAME_2 = "b"
        assert len(df_ds.filter((COLUMN_NAME_1, 1, Operator.EQUAL))) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] == 1]
        )
        assert len(df_ds.filter((COLUMN_NAME_1, 1, Operator.NOT_EQUAL))) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] != 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, 1, Operator.EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] == 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, 1, Operator.NOT_EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] != 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, 1, Operator.LESS_THAN)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] < 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, 1, Operator.LESS_OR_EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] <= 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, 1, Operator.GREATER_THAN)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] > 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, 1, Operator.GREATER_OR_EQUAL)])) == len(
            default_data_frame[default_data_frame[COLUMN_NAME_1] >= 1]
        )
        assert len(df_ds.filter([(COLUMN_NAME_1, -1000, Operator.LESS_OR_EQUAL)])) == 0
        assert len(df_ds.filter([(COLUMN_NAME_1, 1000, Operator.GREATER_OR_EQUAL)])) == 0
        assert len(df_ds.filter([(COLUMN_NAME_1, 4, Operator.EQUAL), (COLUMN_NAME_1, 5, Operator.EQUAL)])) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] == 4) & (default_data_frame[COLUMN_NAME_1] == 5)]
        )
        assert len(
            df_ds.filter([(COLUMN_NAME_1, 4, Operator.EQUAL), (COLUMN_NAME_2, 5, Operator.EQUAL)], JoinOperator.OR)
        ) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] == 4) | (default_data_frame[COLUMN_NAME_2] == 5)]
        )
        assert len(
            df_ds.filter(
                [(COLUMN_NAME_1, 1, Operator.GREATER_THAN), (COLUMN_NAME_2, 3, Operator.GREATER_THAN)], JoinOperator.AND
            )
        ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 1) & (default_data_frame[COLUMN_NAME_2] > 3)])
        assert len(
            df_ds.filter(
                [(COLUMN_NAME_1, 2, Operator.GREATER_THAN), (COLUMN_NAME_1, 3, Operator.GREATER_THAN)], JoinOperator.OR
            )
        ) == len(default_data_frame[(default_data_frame[COLUMN_NAME_1] > 2) | (default_data_frame[COLUMN_NAME_1] > 3)])
        assert len(
            df_ds.filter(
                [(COLUMN_NAME_1, 10, Operator.GREATER_THAN), (COLUMN_NAME_1, -10, Operator.LESS_THAN)], JoinOperator.AND
            )
        ) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] > 10) | (default_data_frame[COLUMN_NAME_1] < -10)]
        )
        assert len(
            df_ds.filter(
                [(COLUMN_NAME_1, 10, Operator.GREATER_THAN), (COLUMN_NAME_1, -10, Operator.LESS_THAN)], JoinOperator.OR
            )
        ) == len(
            default_data_frame[(default_data_frame[COLUMN_NAME_1] > 10) | (default_data_frame[COLUMN_NAME_1] < -10)]
        )
        list_ds = FakeListDataNode("fake list ds")

        KEY_NAME = "value"

        assert len(list_ds.filter((KEY_NAME, 4, Operator.EQUAL))) == 1
        assert len(list_ds.filter((KEY_NAME, 4, Operator.NOT_EQUAL))) == 9
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.EQUAL)])) == 1
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.NOT_EQUAL)])) == 9
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.LESS_THAN)])) == 4
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.LESS_OR_EQUAL)])) == 5
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.GREATER_THAN)])) == 5
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.GREATER_OR_EQUAL)])) == 6
        assert len(list_ds.filter([(KEY_NAME, -1000, Operator.LESS_OR_EQUAL)])) == 0
        assert len(list_ds.filter([(KEY_NAME, 1000, Operator.GREATER_OR_EQUAL)])) == 0

        assert len(list_ds.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 5, Operator.EQUAL)])) == 0
        assert len(list_ds.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 5, Operator.EQUAL)], JoinOperator.OR)) == 2
        assert (
            len(list_ds.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 11, Operator.EQUAL)], JoinOperator.AND)) == 0
        )
        assert (
            len(list_ds.filter([(KEY_NAME, 4, Operator.EQUAL), (KEY_NAME, 11, Operator.EQUAL)], JoinOperator.OR)) == 1
        )

        assert (
            len(list_ds.filter([(KEY_NAME, -10, Operator.LESS_OR_EQUAL), (KEY_NAME, 11, Operator.GREATER_OR_EQUAL)]))
            == 0
        )
        assert (
            len(
                list_ds.filter(
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
                list_ds.filter(
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
                list_ds.filter(
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
        dm = DataManager()
        ds = FakeDataNode("foo")

        dm.set(ds)
        assert not dm.get(ds.id).is_ready_for_reading
        ds.write("Any data")

        assert ds.is_ready_for_reading
        assert dm.get(ds.id).is_ready_for_reading
