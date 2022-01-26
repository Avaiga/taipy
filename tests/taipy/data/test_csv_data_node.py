import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.common.alias import DataNodeId
from taipy.data import CSVDataNode
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty
from taipy.exceptions.data_node import NoData


class TestCSVDataNode:
    def test_create(self):
        path = "data/node/path"
        ds = CSVDataNode("fOo BAr", Scope.PIPELINE, name="super name", properties={"path": path, "has_header": False})
        assert isinstance(ds, CSVDataNode)
        assert ds.storage_type() == "csv"
        assert ds.config_name == "foo_bar"
        assert ds.name == "super name"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.parent_id is None
        assert ds.last_edition_date is None
        assert ds.job_ids == []
        assert not ds.is_ready_for_reading
        assert ds.path == path
        assert ds.has_header is False

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE, DataNodeId("ds_id"))
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE, DataNodeId("ds_id"), properties={})
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE, DataNodeId("ds_id"), properties={"has_header": True})

    def test_read_with_header(self):
        not_existing_csv = CSVDataNode("foo", Scope.PIPELINE, properties={"path": "WRONG.csv", "has_header": True})
        with pytest.raises(NoData):
            not_existing_csv.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode without exposed_type (Default is pandas.DataFrame)
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.PIPELINE, properties={"path": path})
        data_pandas = csv_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 10
        assert np.array_equal(data_pandas.to_numpy(), pd.read_csv(path).to_numpy())

        # Create CSVDataNode with numpy exposed_type
        csv_data_node_as_numpy = CSVDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": True, "exposed_type": "numpy"}
        )
        data_numpy = csv_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 10
        assert np.array_equal(data_numpy, pd.read_csv(path).to_numpy())

        # Create the same CSVDataNode but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        csv_data_node_as_custom_object = CSVDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "exposed_type": MyCustomObject}
        )
        data_custom = csv_data_node_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 10

        for (index, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
            assert isinstance(row_custom, MyCustomObject)
            assert row_pandas["id"] == row_custom.id
            assert str(row_pandas["integer"]) == row_custom.integer
            assert row_pandas["text"] == row_custom.text

    def test_read_without_header(self):
        not_existing_csv = CSVDataNode("foo", Scope.PIPELINE, properties={"path": "WRONG.csv", "has_header": False})
        with pytest.raises(NoData):
            not_existing_csv.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode without exposed_type (Default is pandas.DataFrame)
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.PIPELINE, properties={"path": path, "has_header": False})
        data_pandas = csv_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 11
        assert np.array_equal(data_pandas.to_numpy(), pd.read_csv(path, header=None).to_numpy())

        # Create CSVDataNode with numpy exposed_type
        csv_data_node_as_numpy = CSVDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "exposed_type": "numpy"}
        )
        data_numpy = csv_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 11
        assert np.array_equal(data_numpy, pd.read_csv(path, header=None).to_numpy())

        # Create the same CSVDataNode but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        csv_data_node_as_custom_object = CSVDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "exposed_type": MyCustomObject}
        )
        data_custom = csv_data_node_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 11

        for (index, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
            assert isinstance(row_custom, MyCustomObject)
            assert row_pandas[0] == row_custom.id
            assert str(row_pandas[1]) == row_custom.integer
            assert row_pandas[2] == row_custom.text

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, csv_file, default_data_frame, content, columns):
        csv_ds = CSVDataNode("foo", Scope.PIPELINE, properties={"path": csv_file})
        assert np.array_equal(csv_ds.read().values, default_data_frame.values)
        if not columns:
            csv_ds.write(content)
            df = pd.DataFrame(content)
        else:
            csv_ds.write_with_column_names(content, columns)
            df = pd.DataFrame(content, columns=columns)
        assert np.array_equal(csv_ds.read().values, df.values)

        csv_ds.write(None)
        assert len(csv_ds.read()) == 0
