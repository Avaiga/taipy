import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.core.common.alias import DataNodeId
from taipy.core.config.config import Config
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_manager import DataManager
from taipy.core.data.scope import Scope
from taipy.core.exceptions import MissingRequiredProperty
from taipy.core.exceptions.data_node import NoData


class TestCSVDataNode:
    def test_create(self):
        path = "data/node/path"
        dn = CSVDataNode("fOo BAr", Scope.PIPELINE, name="super name", properties={"path": path, "has_header": False})
        assert isinstance(dn, CSVDataNode)
        assert dn.storage_type() == "csv"
        assert dn.config_name == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.parent_id is None
        assert dn.last_edition_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.has_header is False

    def test_new_csv_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.add_data_node("not_ready_data_node_config_name", "csv", path="NOT_EXISTING.csv")
        not_ready_dn = DataManager.get_or_create(not_ready_dn_cfg)
        assert not not_ready_dn.is_ready_for_reading

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ready_dn_cfg = Config.add_data_node("ready_data_node_config_name", "csv", path=path)
        ready_dn = DataManager.get_or_create(ready_dn_cfg)
        assert ready_dn.is_ready_for_reading

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={})
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={"has_header": True})

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
        csv_dn = CSVDataNode("foo", Scope.PIPELINE, properties={"path": csv_file})
        assert np.array_equal(csv_dn.read().values, default_data_frame.values)
        if not columns:
            csv_dn.write(content)
            df = pd.DataFrame(content)
        else:
            csv_dn.write_with_column_names(content, columns)
            df = pd.DataFrame(content, columns=columns)
        assert np.array_equal(csv_dn.read().values, df.values)

        csv_dn.write(None)
        assert len(csv_dn.read()) == 0
