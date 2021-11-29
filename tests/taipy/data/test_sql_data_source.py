import pytest

from taipy.data import SQLDataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class TestSQLDataSource:
    def test_create(self):
        ds = SQLDataSource(
            "fOo BAr",
            Scope.PIPELINE,
            properties={
                "db_username": "sa",
                "db_password": "foobar",
                "db_name": "datasource",
                "db_engine": "mssql",
                "query": "SELECT * from table_name",
            },
        )
        assert isinstance(ds, SQLDataSource)
        assert ds.storage_type() == "sql"
        assert ds.config_name == "foo_bar"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.parent_id is None
        assert ds.job_ids == []
        assert not ds.up_to_date
        assert ds.query != ""

    @pytest.mark.parametrize(
        "properties",
        [
            {},
            {"db_username": "foo"},
            {"db_username": "foo", "db_password": "foo"},
            {"db_username": "foo", "db_password": "foo", "db_name": "foo"},
        ],
    )
    def test_create_with_missing_parameters(self, properties):
        with pytest.raises(MissingRequiredProperty):
            SQLDataSource("foo", Scope.PIPELINE, "ds_id")
        with pytest.raises(MissingRequiredProperty):
            SQLDataSource("foo", Scope.PIPELINE, "ds_id", properties=properties)
