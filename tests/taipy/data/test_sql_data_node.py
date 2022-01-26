from importlib import util
from unittest import mock

import pandas as pd
import pytest

from taipy.common.alias import DataNodeId
from taipy.data import SQLDataNode
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty

if not util.find_spec("pyodbc"):
    pytest.skip("skipping tests because PyODBC is not installed", allow_module_level=True)


class TestSQLDataNode:
    def test_create(self):
        ds = SQLDataNode(
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
        assert isinstance(ds, SQLDataNode)
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
            SQLDataNode("foo", Scope.PIPELINE, DataNodeId("ds_id"))
        with pytest.raises(MissingRequiredProperty):
            SQLDataNode("foo", Scope.PIPELINE, DataNodeId("ds_id"), properties=properties)

    @mock.patch("taipy.data.sql.SQLDataNode._read_as", return_value="custom")
    @mock.patch("taipy.data.sql.SQLDataNode._read_as_pandas_dataframe", return_value="pandas")
    @mock.patch("taipy.data.sql.SQLDataNode._read_as_numpy", return_value="numpy")
    def test_read(self, mock_read_as, mock_read_as_pandas_dataframe, mock_read_as_numpy):

        # Create SQLDataNode without exposed_type (Default is pandas.DataFrame)
        sql_data_node_as_pandas = SQLDataNode(
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

        assert sql_data_node_as_pandas._read() == "pandas"

        # Create the same SQLDataNode but with custom exposed_type
        sql_data_node_as_custom_object = SQLDataNode(
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
        assert sql_data_node_as_custom_object._read() == "custom"

        # Create the same SQLDataSource but with numpy exposed_type
        sql_data_source_as_numpy_object = SQLDataNode(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "a",
                "db_password": "a",
                "db_name": "a",
                "db_engine": "mssql",
                "read_query": "SELECT * from table_name",
                "write_table": "foo",
                "exposed_type": "numpy",
            },
        )

        assert sql_data_source_as_numpy_object._read() == "numpy"

    def test_read_as(self):
        class MyCustomObject:
            def __init__(self, foo=None, bar=None, *args, **kwargs):
                self.foo = foo
                self.bar = bar
                self.args = args
                self.kwargs = kwargs

        sql_data_node = SQLDataNode(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "sa",
                "db_password": "foobar",
                "db_name": "datanode",
                "db_engine": "mssql",
                "read_query": "SELECT * from table_name",
                "write_table": "foo",
            },
        )

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.dispatch.return_value = [
                {"foo": "baz", "bar": "qux"},
                {"foo": "quux", "bar": "quuz"},
                {"foo": "corge"},
                {"bar": "grault"},
                {"KWARGS_KEY": "KWARGS_VALUE"},
                {},
            ]
            data = sql_data_node._read_as("fake query", MyCustomObject)

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
            cursor_mock.dispatch.return_value = []
            data_2 = sql_data_node._read_as("fake query", MyCustomObject)
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
        ds = SQLDataNode(
            "foo",
            Scope.PIPELINE,
            properties={
                "db_username": "sa",
                "db_password": "foobar",
                "db_name": "datanode",
                "db_engine": "mssql",
                "read_query": "SELECT * from foo",
                "write_table": "foo",
            },
        )

        with mock.patch("sqlalchemy.engine.Engine.connect") as engine_mock:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.dispatch.return_value = None
            ds._write(data)
