from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import pytest

from taipy.common.alias import DataSourceId, JobId
from taipy.data import DataSource, InMemoryDataSource, Scope
from taipy.data.operator import Operator
from taipy.exceptions.data_source import NoData


class FakeDataSource(DataSource):
    read_has_been_called = 0
    write_has_been_called = 0

    def __init__(self, config_name, **kwargs):
        super().__init__(config_name, **kwargs)

    def _read(self, query=None):
        self.read_has_been_called += 1

    def _write(self, data):
        self.write_has_been_called += 1


class FakeDataframeDataSource(DataSource):
    COLUMN_NAME = "col_1"
    data = pd.DataFrame({COLUMN_NAME: [i for i in range(3)]})

    def __init__(self, config_name, **kwargs):
        super().__init__(config_name, **kwargs)

    def _read(self, query=None):
        return self.data

    def _write(self, data):
        self.data = self.data.append({self.COLUMN_NAME: self.data.iloc[-1][self.COLUMN_NAME] + 1}, ignore_index=True)


class TestDataSource:
    def test_create_with_default_values(self):
        ds = DataSource("fOo BAr")
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
        ds = DataSource(
            "fOo BAr é@",
            Scope.SCENARIO,
            DataSourceId("an_id"),
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
        ds = FakeDataSource("fOo BAr")
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
        ds = DataSource("fOo BAr")
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
        ds = InMemoryDataSource("foo", Scope.PIPELINE, DataSourceId("id"), "name", "parent_id")
        assert ds.is_up_to_date is False

        # test has been writen
        ds.write("My data")
        assert ds.is_up_to_date is True

    def test_is_up_to_date_with_30_min_validity_period(self):
        # Test Never been writen
        ds = InMemoryDataSource("foo", Scope.PIPELINE, DataSourceId("id"), "name", "parent_id", validity_minutes=30)
        assert ds.is_up_to_date is False

        # Has been writen less than 30 minutes ago
        ds.write("My data")
        assert ds.is_up_to_date is True

        # Has been writen more than 30 minutes ago
        ds.last_edition_date = datetime.now() + timedelta(days=-1)
        assert ds.is_up_to_date is False

    def test_filter(self):
        ds = FakeDataSource("fake ds")
        ds.write("Any data")

        assert NotImplemented == ds.filter("any", 0, Operator.EQUAL)
        assert NotImplemented == ds.filter("any", 0, Operator.LESSER)
        assert NotImplemented == ds.filter("any", 0, Operator.GREATER)

        df_ds = FakeDataframeDataSource("fake dataframe ds")
        df_ds.write("Any data")

        assert len(df_ds.filter(df_ds.COLUMN_NAME, 1, Operator.EQUAL)) == 1
        assert len(df_ds.filter(df_ds.COLUMN_NAME, 1, Operator.GREATER)) == 2
        assert len(df_ds.filter(df_ds.COLUMN_NAME, 1, Operator.LESSER)) == 1
