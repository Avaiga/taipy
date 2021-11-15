from datetime import datetime
from time import sleep

import pytest

from taipy.common.alias import JobId
from taipy.data import DataSource, Scope
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
        assert not ds.up_to_date
        assert len(ds.properties) == 0

    def test_create(self):
        a_date = datetime.now()
        ds = DataSource(
            "fOo BAr é@",
            Scope.SCENARIO,
            "an_id",
            "a name",
            "a_scenario_id",
            a_date,
            [JobId("a_job_id")],
            True,
            prop="erty",
        )
        assert ds.config_name == "foo_bar_e-"
        assert ds.scope == Scope.SCENARIO
        assert ds.id == "an_id"
        assert ds.name == "a name"
        assert ds.parent_id == "a_scenario_id"
        assert ds.last_edition_date == a_date
        assert ds.job_ids == ["a_job_id"]
        assert ds.up_to_date
        assert len(ds.properties) == 1
        assert ds.properties["prop"] == "erty"

    def test_read_write(self):
        ds = FakeDataSource("fOo BAr")
        with pytest.raises(NoData):
            ds.read()
        assert ds.write_has_been_called == 0
        assert ds.read_has_been_called == 0
        assert not ds.up_to_date
        assert ds.last_edition_date is None
        assert ds.job_ids == []

        ds.write("Any data")
        assert ds.write_has_been_called == 1
        assert ds.read_has_been_called == 0
        assert ds.last_edition_date is not None
        first_edition = ds.last_edition_date
        assert ds.up_to_date
        assert ds.job_ids == []
        sleep(0.1)

        ds.write("Any other data", job_id := JobId("a_job_id"))
        assert ds.write_has_been_called == 2
        assert ds.read_has_been_called == 0
        second_edition = ds.last_edition_date
        assert first_edition < second_edition
        assert ds.up_to_date
        assert ds.job_ids == [job_id]

        ds.read()
        assert ds.write_has_been_called == 2
        assert ds.read_has_been_called == 1
        second_edition = ds.last_edition_date
        assert first_edition < second_edition
        assert ds.up_to_date
        assert ds.job_ids == [job_id]

    def test_updated(self):
        ds = DataSource("fOo BAr")
        assert ds.last_edition_date is None
        assert not ds.up_to_date
        assert ds.job_ids == []

        ds.updated(a_date := datetime.now(), job_id := JobId("a_job_id"))
        assert ds.last_edition_date == a_date
        assert ds.up_to_date
        assert ds.job_ids == [job_id]
