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

import os
import pathlib
from datetime import datetime
from time import sleep

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
import pytest

from src.taipy.core.common.alias import DataNodeId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.exceptions.exceptions import InvalidExposedType, MissingRequiredProperty, NoData
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")
    if os.path.isfile(path):
        os.remove(path)


class MyCustomObject:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


class TestCSVDataNode:
    def test_create(self):
        path = "data/node/path"
        dn = CSVDataNode("foo_bar", Scope.PIPELINE, name="super name", properties={"path": path, "has_header": False})
        assert isinstance(dn, CSVDataNode)
        assert dn.storage_type() == "csv"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edition_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.has_header is False
        assert dn.exposed_type == "pandas"

        with pytest.raises(InvalidConfigurationId):
            dn = CSVDataNode(
                "foo bar", Scope.PIPELINE, name="super name", properties={"path": path, "has_header": False}
            )

    def test_new_csv_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node("not_ready_data_node_config_id", "csv", path="NOT_EXISTING.csv")
        not_ready_dn = _DataManager._bulk_get_or_create([not_ready_dn_cfg])[not_ready_dn_cfg]
        assert not not_ready_dn.is_ready_for_reading

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "csv", path=path)
        ready_dn = _DataManager._bulk_get_or_create([ready_dn_cfg])[ready_dn_cfg]
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
            assert not_existing_csv.read() is None
            not_existing_csv.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # # Create CSVDataNode without exposed_type (Default is pandas.DataFrame)
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.PIPELINE, properties={"path": path})
        data_pandas = csv_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 10
        assert np.array_equal(data_pandas.to_numpy(), pd.read_csv(path).to_numpy())

        # Create CSVDataNode with modin exposed_type
        csv_data_node_as_modin = CSVDataNode("bar", Scope.PIPELINE, properties={"path": path, "exposed_type": "modin"})
        data_modin = csv_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 10
        assert np.array_equal(data_modin.to_numpy(), pd.read_csv(path).to_numpy())

        # Create CSVDataNode with numpy exposed_type
        csv_data_node_as_numpy = CSVDataNode(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": True, "exposed_type": "numpy"}
        )
        data_numpy = csv_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 10
        assert np.array_equal(data_numpy, pd.read_csv(path).to_numpy())

        # Create the same CSVDataNode but with custom exposed_type
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
            assert not_existing_csv.read() is None
            not_existing_csv.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode without exposed_type (Default is pandas.DataFrame)
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.PIPELINE, properties={"path": path, "has_header": False})
        data_pandas = csv_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 11
        assert np.array_equal(data_pandas.to_numpy(), pd.read_csv(path, header=None).to_numpy())

        # Create CSVDataNode with modin exposed_type
        csv_data_node_as_modin = CSVDataNode(
            "baz", Scope.PIPELINE, properties={"path": path, "has_header": False, "exposed_type": "modin"}
        )
        data_modin = csv_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 11
        assert np.array_equal(data_modin.to_numpy(), modin_pd.read_csv(path, header=None).to_numpy())

        # Create CSVDataNode with numpy exposed_type
        csv_data_node_as_numpy = CSVDataNode(
            "qux", Scope.PIPELINE, properties={"path": path, "has_header": False, "exposed_type": "numpy"}
        )
        data_numpy = csv_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 11
        assert np.array_equal(data_numpy, pd.read_csv(path, header=None).to_numpy())

        # Create the same CSVDataNode but with custom exposed_type
        csv_data_node_as_custom_object = CSVDataNode(
            "quux", Scope.PIPELINE, properties={"path": path, "has_header": False, "exposed_type": MyCustomObject}
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

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write_modin(self, csv_file, default_data_frame, content, columns):
        default_data_frame = modin_pd.DataFrame(default_data_frame)
        csv_dn = CSVDataNode("foo", Scope.PIPELINE, properties={"path": csv_file, "exposed_type": "modin"})
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

    def test_set_path(self):
        dn = CSVDataNode("foo", Scope.PIPELINE, properties={"default_path": "foo.csv"})
        assert dn.path == "foo.csv"
        dn.path = "bar.csv"
        assert dn.path == "bar.csv"

    def test_raise_error_when_path_not_exist(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataNode("foo", Scope.PIPELINE)

    def test_read_write_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")
        dn = CSVDataNode("foo", Scope.PIPELINE, properties={"default_path": path})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write(read_data)
        assert dn.read().equals(read_data)

    def test_pandas_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        dn = CSVDataNode("foo", Scope.PIPELINE, properties={"path": path, "exposed_type": "pandas"})
        assert isinstance(dn.read(), pd.DataFrame)

    def test_raise_error_invalid_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        with pytest.raises(InvalidExposedType):
            CSVDataNode("foo", Scope.PIPELINE, properties={"path": path, "exposed_type": "foo"})

    def test_get_system_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.csv"))
        pd.DataFrame([]).to_csv(temp_file_path)
        dn = CSVDataNode("foo", Scope.PIPELINE, properties={"path": temp_file_path, "exposed_type": "pandas"})

        dn.write(pd.DataFrame([1, 2, 3]))
        previous_edit_date = dn.last_edit_date

        sleep(0.1)

        pd.DataFrame([4, 5, 6]).to_csv(temp_file_path)
        new_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

        assert previous_edit_date < dn.last_edit_date
        assert new_edit_date == dn.last_edit_date

        sleep(0.1)

        dn.write(pd.DataFrame([7, 8, 9]))
        assert new_edit_date < dn.last_edit_date
        os.unlink(temp_file_path)
