# Copyright 2021-2024 Avaiga Private Limited
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
from modin.pandas.test.utils import df_equals
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.exceptions.exceptions import InvalidExposedType, NoData


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
        dn = CSVDataNode(
            "foo_bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "name": "super name"}
        )
        assert isinstance(dn, CSVDataNode)
        assert dn.storage_type() == "csv"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path
        assert dn.has_header is False
        assert dn.exposed_type == "pandas"

        with pytest.raises(InvalidConfigurationId):
            dn = CSVDataNode(
                "foo bar", Scope.SCENARIO, properties={"path": path, "has_header": False, "name": "super name"}
            )

    def test_get_user_properties(self, csv_file):
        dn_1 = CSVDataNode("dn_1", Scope.SCENARIO, properties={"path": "data/node/path"})
        assert dn_1._get_user_properties() == {}

        dn_2 = CSVDataNode(
            "dn_2",
            Scope.SCENARIO,
            properties={
                "exposed_type": "numpy",
                "default_data": "foo",
                "default_path": csv_file,
                "has_header": False,
                "foo": "bar",
            },
        )

        # exposed_type, default_data, default_path, path, has_header, sheet_name are filtered out
        assert dn_2._get_user_properties() == {"foo": "bar"}

    def test_new_csv_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node("not_ready_data_node_config_id", "csv", path="NOT_EXISTING.csv")
        not_ready_dn = _DataManager._bulk_get_or_create([not_ready_dn_cfg])[not_ready_dn_cfg]
        assert not not_ready_dn.is_ready_for_reading

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "csv", path=path)
        ready_dn = _DataManager._bulk_get_or_create([ready_dn_cfg])[ready_dn_cfg]
        assert ready_dn.is_ready_for_reading

    @pytest.mark.parametrize(
        ["properties", "exists"],
        [
            ({}, False),
            ({"default_data": ["foo", "bar"]}, True),
        ],
    )
    def test_create_with_default_data(self, properties, exists):
        dn = CSVDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)
        assert os.path.exists(dn.path) is exists

    def test_read_with_header_pandas(self):
        not_existing_csv = CSVDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.csv", "has_header": True})
        with pytest.raises(NoData):
            assert not_existing_csv.read() is None
            not_existing_csv.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # # Create CSVDataNode without exposed_type (Default is pandas.DataFrame)
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.SCENARIO, properties={"path": path})
        data_pandas = csv_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 10
        assert np.array_equal(data_pandas.to_numpy(), pd.read_csv(path).to_numpy())

    @pytest.mark.modin
    def test_read_with_header_modin(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode with modin exposed_type
        csv_data_node_as_modin = CSVDataNode("bar", Scope.SCENARIO, properties={"path": path, "exposed_type": "modin"})
        data_modin = csv_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 10
        assert np.array_equal(data_modin.to_numpy(), modin_pd.read_csv(path).to_numpy())

    def test_read_with_header_numpy(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode with numpy exposed_type
        csv_data_node_as_numpy = CSVDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "has_header": True, "exposed_type": "numpy"}
        )
        data_numpy = csv_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 10
        assert np.array_equal(data_numpy, pd.read_csv(path).to_numpy())

    def test_read_with_header_custom_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.SCENARIO, properties={"path": path})
        data_pandas = csv_data_node_as_pandas.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create the same CSVDataNode but with custom exposed_type
        csv_data_node_as_custom_object = CSVDataNode(
            "bar", Scope.SCENARIO, properties={"path": path, "exposed_type": MyCustomObject}
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
        not_existing_csv = CSVDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.csv", "has_header": False})
        with pytest.raises(NoData):
            assert not_existing_csv.read() is None
            not_existing_csv.read_or_raise()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode without exposed_type (Default is pandas.DataFrame)
        csv_data_node_as_pandas = CSVDataNode("bar", Scope.SCENARIO, properties={"path": path, "has_header": False})
        data_pandas = csv_data_node_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 11
        assert np.array_equal(data_pandas.to_numpy(), pd.read_csv(path, header=None).to_numpy())

        # Create CSVDataNode with numpy exposed_type
        csv_data_node_as_numpy = CSVDataNode(
            "qux", Scope.SCENARIO, properties={"path": path, "has_header": False, "exposed_type": "numpy"}
        )
        data_numpy = csv_data_node_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 11
        assert np.array_equal(data_numpy, pd.read_csv(path, header=None).to_numpy())

        # Create the same CSVDataNode but with custom exposed_type
        csv_data_node_as_custom_object = CSVDataNode(
            "quux", Scope.SCENARIO, properties={"path": path, "has_header": False, "exposed_type": MyCustomObject}
        )
        data_custom = csv_data_node_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 11

        for (index, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
            assert isinstance(row_custom, MyCustomObject)
            assert row_pandas[0] == row_custom.id
            assert str(row_pandas[1]) == row_custom.integer
            assert row_pandas[2] == row_custom.text

    @pytest.mark.modin
    def test_read_without_header_modin(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        # Create CSVDataNode with modin exposed_type
        csv_data_node_as_modin = CSVDataNode(
            "baz", Scope.SCENARIO, properties={"path": path, "has_header": False, "exposed_type": "modin"}
        )
        data_modin = csv_data_node_as_modin.read()
        assert isinstance(data_modin, modin_pd.DataFrame)
        assert len(data_modin) == 11
        assert np.array_equal(data_modin.to_numpy(), modin_pd.read_csv(path, header=None).to_numpy())

    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
            ([[11, 22, 33], [44, 55, 66]]),
        ],
    )
    def test_append(self, csv_file, default_data_frame, content):
        csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file})
        assert_frame_equal(csv_dn.read(), default_data_frame)

        csv_dn.append(content)
        assert_frame_equal(
            csv_dn.read(),
            pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(drop=True),
        )

    @pytest.mark.modin
    @pytest.mark.parametrize(
        "content",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}]),
            (pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])),
            ([[11, 22, 33], [44, 55, 66]]),
        ],
    )
    def test_append_modin(self, csv_file, default_data_frame, content):
        csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "modin"})
        df_equals(csv_dn.read(), modin_pd.DataFrame(default_data_frame))

        csv_dn.append(content)
        df_equals(
            csv_dn.read(),
            modin_pd.concat([default_data_frame, pd.DataFrame(content, columns=["a", "b", "c"])]).reset_index(
                drop=True
            ),
        )

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, csv_file, default_data_frame, content, columns):
        csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file})
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

    def test_write_with_different_encoding(self, csv_file):
        data = pd.DataFrame([{"≥a": 1, "b": 2}])

        utf8_dn = CSVDataNode("utf8_dn", Scope.SCENARIO, properties={"default_path": csv_file})
        utf16_dn = CSVDataNode("utf16_dn", Scope.SCENARIO, properties={"default_path": csv_file, "encoding": "utf-16"})

        # If a file is written with utf-8 encoding, it can only be read with utf-8, not utf-16 encoding
        utf8_dn.write(data)
        assert np.array_equal(utf8_dn.read(), data)
        with pytest.raises(UnicodeError):
            utf16_dn.read()

        # If a file is written with utf-16 encoding, it can only be read with utf-16, not utf-8 encoding
        utf16_dn.write(data)
        assert np.array_equal(utf16_dn.read(), data)
        with pytest.raises(UnicodeError):
            utf8_dn.read()

    @pytest.mark.modin
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
        csv_dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "modin"})
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

    @pytest.mark.modin
    def test_write_modin_with_different_encoding(self, csv_file):
        data = pd.DataFrame([{"≥a": 1, "b": 2}])

        utf8_dn = CSVDataNode("utf8_dn", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "modin"})
        utf16_dn = CSVDataNode(
            "utf16_dn", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "modin", "encoding": "utf-16"}
        )

        # If a file is written with utf-8 encoding, it can only be read with utf-8, not utf-16 encoding
        utf8_dn.write(data)
        assert np.array_equal(utf8_dn.read(), data)
        with pytest.raises(UnicodeError):
            utf16_dn.read()

        # If a file is written with utf-16 encoding, it can only be read with utf-16, not utf-8 encoding
        utf16_dn.write(data)
        assert np.array_equal(utf16_dn.read(), data)
        with pytest.raises(UnicodeError):
            utf8_dn.read()

    def test_set_path(self):
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"default_path": "foo.csv"})
        assert dn.path == "foo.csv"
        dn.path = "bar.csv"
        assert dn.path == "bar.csv"

    def test_read_write_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.csv")
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"default_path": path})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write(read_data)
        assert dn.read().equals(read_data)

    def test_pandas_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "pandas"})
        assert isinstance(dn.read(), pd.DataFrame)

    def test_filter_pandas_exposed_type(self, csv_file):
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "pandas"})
        dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
            ]
        )

        # Test datanode indexing and slicing
        assert dn["foo"].equals(pd.Series([1, 1, 1, 2, None]))
        assert dn["bar"].equals(pd.Series([1, 2, None, 2, 2]))
        assert dn[:2].equals(pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

        # Test filter data
        filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
        filtered_by_indexing = dn[dn["foo"] == 1]
        expected_data = pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}, {"foo": 1.0}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
        filtered_by_indexing = dn[dn["foo"] != 1]
        expected_data = pd.DataFrame([{"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("bar", 2, Operator.EQUAL))
        filtered_by_indexing = dn[dn["bar"] == 2]
        expected_data = pd.DataFrame([{"foo": 1.0, "bar": 2.0}, {"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
        filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
        expected_data = pd.DataFrame(
            [
                {"foo": 1.0, "bar": 1.0},
                {"foo": 1.0, "bar": 2.0},
                {"foo": 2.0, "bar": 2.0},
                {"bar": 2.0},
            ]
        )
        assert_frame_equal(filtered_by_filter_method.reset_index(drop=True), expected_data)
        assert_frame_equal(filtered_by_indexing.reset_index(drop=True), expected_data)

    @pytest.mark.modin
    def test_filter_modin_exposed_type(self, csv_file):
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "modin"})
        dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
            ]
        )

        # Test datanode indexing and slicing
        assert dn["foo"].equals(modin_pd.Series([1, 1, 1, 2, None]))
        assert dn["bar"].equals(modin_pd.Series([1, 2, None, 2, 2]))
        assert dn[:2].equals(modin_pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}]))

        # Test filter data
        filtered_by_filter_method = dn.filter(("foo", 1, Operator.EQUAL))
        filtered_by_indexing = dn[dn["foo"] == 1]
        expected_data = modin_pd.DataFrame([{"foo": 1.0, "bar": 1.0}, {"foo": 1.0, "bar": 2.0}, {"foo": 1.0}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("foo", 1, Operator.NOT_EQUAL))
        filtered_by_indexing = dn[dn["foo"] != 1]
        expected_data = modin_pd.DataFrame([{"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter(("bar", 2, Operator.EQUAL))
        filtered_by_indexing = dn[dn["bar"] == 2]
        expected_data = modin_pd.DataFrame([{"foo": 1.0, "bar": 2.0}, {"foo": 2.0, "bar": 2.0}, {"bar": 2.0}])
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

        filtered_by_filter_method = dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)
        filtered_by_indexing = dn[(dn["bar"] == 1) | (dn["bar"] == 2)]
        expected_data = modin_pd.DataFrame(
            [
                {"foo": 1.0, "bar": 1.0},
                {"foo": 1.0, "bar": 2.0},
                {"foo": 2.0, "bar": 2.0},
                {"bar": 2.0},
            ]
        )
        df_equals(filtered_by_filter_method.reset_index(drop=True), expected_data)
        df_equals(filtered_by_indexing.reset_index(drop=True), expected_data)

    def test_filter_numpy_exposed_type(self, csv_file):
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": csv_file, "exposed_type": "numpy"})
        dn.write(
            [
                [1, 1],
                [1, 2],
                [1, 3],
                [2, 1],
                [2, 2],
                [2, 3],
            ]
        )

        # Test datanode indexing and slicing
        assert np.array_equal(dn[0], np.array([1, 1]))
        assert np.array_equal(dn[1], np.array([1, 2]))
        assert np.array_equal(dn[:3], np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn[:, 0], np.array([1, 1, 1, 2, 2, 2]))
        assert np.array_equal(dn[1:4, :1], np.array([[1], [1], [2]]))

        # Test filter data
        assert np.array_equal(dn.filter((0, 1, Operator.EQUAL)), np.array([[1, 1], [1, 2], [1, 3]]))
        assert np.array_equal(dn[dn[:, 0] == 1], np.array([[1, 1], [1, 2], [1, 3]]))

        assert np.array_equal(dn.filter((0, 1, Operator.NOT_EQUAL)), np.array([[2, 1], [2, 2], [2, 3]]))
        assert np.array_equal(dn[dn[:, 0] != 1], np.array([[2, 1], [2, 2], [2, 3]]))

        assert np.array_equal(dn.filter((1, 2, Operator.EQUAL)), np.array([[1, 2], [2, 2]]))
        assert np.array_equal(dn[dn[:, 1] == 2], np.array([[1, 2], [2, 2]]))

        assert np.array_equal(
            dn.filter([(1, 1, Operator.EQUAL), (1, 2, Operator.EQUAL)], JoinOperator.OR),
            np.array([[1, 1], [1, 2], [2, 1], [2, 2]]),
        )
        assert np.array_equal(dn[(dn[:, 1] == 1) | (dn[:, 1] == 2)], np.array([[1, 1], [1, 2], [2, 1], [2, 2]]))

    def test_raise_error_invalid_exposed_type(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        with pytest.raises(InvalidExposedType):
            CSVDataNode("foo", Scope.SCENARIO, properties={"path": path, "exposed_type": "foo"})

    def test_get_system_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.csv"))
        pd.DataFrame([]).to_csv(temp_file_path)
        dn = CSVDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "pandas"})

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
