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

import dataclasses
import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.common.config.common.scope import Scope
from taipy.core.data.csv import CSVDataNode
from taipy.core.exceptions.exceptions import NoData

csv_file_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")


@dataclasses.dataclass
class MyCustomObject:
    id: int
    integer: int
    text: str


def test_raise_no_data_with_header():
    not_existing_csv = CSVDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.csv", "has_header": True})
    with pytest.raises(NoData):
        assert not_existing_csv.read() is None
        not_existing_csv.read_or_raise()


def test_read_with_header_pandas():
    csv_data_node_as_pandas = CSVDataNode("bar", Scope.SCENARIO, properties={"path": csv_file_path})
    data_pandas = csv_data_node_as_pandas.read()
    assert isinstance(data_pandas, pd.DataFrame)
    assert len(data_pandas) == 10
    assert pd.DataFrame.equals(data_pandas, pd.read_csv(csv_file_path))


def test_read_with_header_numpy():
    csv_data_node_as_numpy = CSVDataNode(
        "bar", Scope.SCENARIO, properties={"path": csv_file_path, "has_header": True, "exposed_type": "numpy"}
    )
    data_numpy = csv_data_node_as_numpy.read()
    assert isinstance(data_numpy, np.ndarray)
    assert len(data_numpy) == 10
    assert np.array_equal(data_numpy, pd.read_csv(csv_file_path).to_numpy())


def test_read_with_header_custom_exposed_type():
    data_pandas = pd.read_csv(csv_file_path)

    csv_data_node_as_custom_object = CSVDataNode(
        "bar", Scope.SCENARIO, properties={"path": csv_file_path, "exposed_type": MyCustomObject}
    )
    data_custom = csv_data_node_as_custom_object.read()
    assert isinstance(data_custom, list)
    assert len(data_custom) == 10

    for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
        assert isinstance(row_custom, MyCustomObject)
        assert row_pandas["id"] == row_custom.id
        assert str(row_pandas["integer"]) == row_custom.integer
        assert row_pandas["text"] == row_custom.text


def test_raise_no_data_without_header():
    not_existing_csv = CSVDataNode("foo", Scope.SCENARIO, properties={"path": "WRONG.csv", "has_header": False})
    with pytest.raises(NoData):
        assert not_existing_csv.read() is None
        not_existing_csv.read_or_raise()


def test_read_without_header_pandas():
    csv_data_node_as_pandas = CSVDataNode(
        "bar", Scope.SCENARIO, properties={"path": csv_file_path, "has_header": False}
    )
    data_pandas = csv_data_node_as_pandas.read()
    assert isinstance(data_pandas, pd.DataFrame)
    assert len(data_pandas) == 11
    assert pd.DataFrame.equals(data_pandas, pd.read_csv(csv_file_path, header=None))


def test_read_without_header_numpy():
    csv_data_node_as_numpy = CSVDataNode(
        "qux", Scope.SCENARIO, properties={"path": csv_file_path, "has_header": False, "exposed_type": "numpy"}
    )
    data_numpy = csv_data_node_as_numpy.read()
    assert isinstance(data_numpy, np.ndarray)
    assert len(data_numpy) == 11
    assert np.array_equal(data_numpy, pd.read_csv(csv_file_path, header=None).to_numpy())


def test_read_without_header_custom_exposed_type():
    csv_data_node_as_custom_object = CSVDataNode(
        "quux", Scope.SCENARIO, properties={"path": csv_file_path, "has_header": False, "exposed_type": MyCustomObject}
    )
    data_custom = csv_data_node_as_custom_object.read()
    assert isinstance(data_custom, list)
    assert len(data_custom) == 11

    data_pandas = pd.read_csv(csv_file_path, header=None)
    for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
        assert isinstance(row_custom, MyCustomObject)
        assert row_pandas[0] == row_custom.id
        assert str(row_pandas[1]) == row_custom.integer
        assert row_pandas[2] == row_custom.text
