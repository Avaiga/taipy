from unittest import mock

import pandas as pd
import pytest

from taipy.common.alias import DataSourceId
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
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mssql",
                "read_query": "SELECT * from daily_min_example",
                "write_table": "foo",
            },
        )
        assert isinstance(ds, SQLDataSource)
        assert ds.storage_type() == "sql"
        assert ds.config_name == "foo_bar"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.parent_id is None
        assert ds.job_ids == []
        assert ds.is_ready_for_reading
        assert ds.read_query != ""

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
            SQLDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"))
        with pytest.raises(MissingRequiredProperty):
            SQLDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties=properties)

    @mock.patch("taipy.data.sql.SQLDataSource._read_as", return_value="custom")
    @mock.patch("taipy.data.sql.SQLDataSource._read_as_pandas_dataframe", return_value="pandas")
    def test_read(self, mock_read_as, mock_read_as_pandas_dataframe):

        # Create SQLDataSource without exposed_type (Default is pandas.DataFrame)
        sql_data_source_as_pandas = SQLDataSource(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "a",
                "db_password": "a",
                "db_name": "a",
                "db_engine": "mssql",
                "read_query": "a",
                "write_table": "foo",
            },
        )

        assert sql_data_source_as_pandas._read() == "pandas"

        # Create the same SQLDataSource but with custom exposed_type
        sql_data_source_as_custom_object = SQLDataSource(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "a",
                "db_password": "a",
                "db_name": "a",
                "db_engine": "mssql",
                "read_query": "SELECT * from table_name",
                "write_table": "foo",
                "exposed_type": "Whatever",
            },
        )
        assert sql_data_source_as_custom_object._read() == "custom"

    def test_read_as(self):
        class MyCustomObject:
            def __init__(self, foo=None, bar=None, *args, **kwargs):
                self.foo = foo
                self.bar = bar
                self.args = args
                self.kwargs = kwargs

        sql_data_source = SQLDataSource(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "sa",
                "db_password": "foobar",
                "db_name": "datasource",
                "db_engine": "mssql",
                "read_query": "SELECT * from table_name",
                "write_table": "foo",
            },
        )

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.return_value = [
                {"foo": "baz", "bar": "qux"},
                {"foo": "quux", "bar": "quuz"},
                {"foo": "corge"},
                {"bar": "grault"},
                {"KWARGS_KEY": "KWARGS_VALUE"},
                {},
            ]
            data = sql_data_source._read_as("fake query", MyCustomObject)

        assert isinstance(data, list)
        assert isinstance(data[0], MyCustomObject)
        assert isinstance(data[1], MyCustomObject)
        assert isinstance(data[2], MyCustomObject)
        assert isinstance(data[3], MyCustomObject)
        assert isinstance(data[4], MyCustomObject)
        assert isinstance(data[5], MyCustomObject)

        assert data[0].foo == "baz"
        assert data[0].bar == "qux"
        assert data[1].foo == "quux"
        assert data[1].bar == "quuz"
        assert data[2].foo == "corge"
        assert data[2].bar is None
        assert data[3].foo is None
        assert data[3].bar == "grault"
        assert data[4].foo is None
        assert data[4].bar is None
        assert data[4].kwargs["KWARGS_KEY"] == "KWARGS_VALUE"
        assert data[5].foo is None
        assert data[5].bar is None
        assert len(data[5].args) == 0
        assert len(data[5].kwargs) == 0

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.return_value = []
            data_2 = sql_data_source._read_as("fake query", MyCustomObject)
        assert isinstance(data_2, list)
        assert len(data_2) == 0

    @pytest.mark.parametrize(
        "data",
        [
            pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}]),
            [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
            {"a": 1, "b": 2},
            [(1, 2), (3, 4)],
            (1, 2),
            [1, 2, 3, 4],
            "foo",
            None,
        ],
    )
    def test_write(self, data):
        ds = SQLDataSource(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "sa",
                "db_password": "foobar",
                "db_name": "datasource",
                "db_engine": "mssql",
                "read_query": "SELECT * from foo",
                "write_table": "foo",
            },
        )

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.return_value = None
            ds._write(data)
