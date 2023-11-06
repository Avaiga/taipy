# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import datetime
import json
import os
import pathlib
from dataclasses import dataclass
from enum import Enum
from time import sleep

import numpy as np
import pandas as pd
import pytest

from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.data_node_id import DataNodeId
from src.taipy.core.data.json import JSONDataNode
from src.taipy.core.data.operator import JoinOperator, Operator
from src.taipy.core.exceptions.exceptions import NoData
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.json")
    if os.path.isfile(path):
        os.remove(path)


class MyCustomObject:
    def __init__(self, id, integer, text):
        self.id = id
        self.integer = integer
        self.text = text


class MyCustomObject2:
    def __init__(self, id, boolean, text):
        self.id = id
        self.boolean = boolean
        self.text = text


class MyEnum(Enum):
    A = 1
    B = 2
    C = 3


@dataclass
class CustomDataclass:
    integer: int
    string: str


class MyCustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, MyCustomObject):
            return {"__type__": "MyCustomObject", "id": o.id, "integer": o.integer, "text": o.text}
        return super().default(self, o)


class MyCustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o):
        if o.get("__type__") == "MyCustomObject":
            return MyCustomObject(o["id"], o["integer"], o["text"])
        else:
            return o


class TestJSONDataNode:
    def test_create(self):
        path = "data/node/path"
        dn = JSONDataNode("foo_bar", Scope.SCENARIO, properties={"default_path": path, "name": "super name"})
        assert isinstance(dn, JSONDataNode)
        assert dn.storage_type() == "json"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path

        with pytest.raises(InvalidConfigurationId):
            dn = JSONDataNode(
                "foo bar", Scope.SCENARIO, properties={"default_path": path, "has_header": False, "name": "super name"}
            )

    def test_get_user_properties(self, json_file):
        dn_1 = JSONDataNode("dn_1", Scope.SCENARIO, properties={"path": json_file})
        assert dn_1._get_user_properties() == {}

        dn_2 = JSONDataNode(
            "dn_2",
            Scope.SCENARIO,
            properties={
                "default_data": "foo",
                "default_path": json_file,
                "encoder": MyCustomEncoder,
                "decoder": MyCustomDecoder,
                "foo": "bar",
            },
        )

        # default_data, default_path, path, encoder, decoder are filtered out
        assert dn_2._get_user_properties() == {"foo": "bar"}

    def test_new_json_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node(
            "not_ready_data_node_config_id", "json", default_path="NOT_EXISTING.json"
        )
        not_ready_dn = _DataManager._bulk_get_or_create([not_ready_dn_cfg])[not_ready_dn_cfg]
        assert not not_ready_dn.is_ready_for_reading
        assert not_ready_dn.path == "NOT_EXISTING.json"

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_list.json")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "json", default_path=path)
        ready_dn = _DataManager._bulk_get_or_create([ready_dn_cfg])[ready_dn_cfg]
        assert ready_dn.is_ready_for_reading

    def test_read_non_existing_json(self):
        not_existing_json = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": "WRONG.json"})
        with pytest.raises(NoData):
            assert not_existing_json.read() is None
            not_existing_json.read_or_raise()

    def test_read(self):
        path_1 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_list.json")
        dn_1 = JSONDataNode("bar", Scope.SCENARIO, properties={"default_path": path_1})
        data_1 = dn_1.read()
        assert isinstance(data_1, list)
        assert len(data_1) == 4

        path_2 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_dict.json")
        dn_2 = JSONDataNode("bar", Scope.SCENARIO, properties={"default_path": path_2})
        data_2 = dn_2.read()
        assert isinstance(data_2, dict)
        assert data_2["id"] == "1"

        path_3 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_int.json")
        dn_3 = JSONDataNode("bar", Scope.SCENARIO, properties={"default_path": path_3})
        data_3 = dn_3.read()
        assert isinstance(data_3, int)
        assert data_3 == 1

        path_4 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_null.json")
        dn_4 = JSONDataNode("bar", Scope.SCENARIO, properties={"default_path": path_4})
        data_4 = dn_4.read()
        assert data_4 is None

    def test_read_invalid_json(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/invalid.json.txt")
        dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": path})
        with pytest.raises(ValueError):
            dn.read()

    def test_write(self, json_file):
        json_dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": json_file})
        data = {"a": 1, "b": 2, "c": 3}
        json_dn.write(data)
        assert np.array_equal(json_dn.read(), data)

    def test_write_with_different_encoding(self, json_file):
        data = {"≥a": 1, "b": 2}

        utf8_dn = JSONDataNode("utf8_dn", Scope.SCENARIO, properties={"default_path": json_file})
        utf16_dn = JSONDataNode(
            "utf16_dn", Scope.SCENARIO, properties={"default_path": json_file, "encoding": "utf-16"}
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

    def test_write_non_serializable(self, json_file):
        json_dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": json_file})
        data = {"a": 1, "b": json_dn}
        with pytest.raises(TypeError):
            json_dn.write(data)

    def test_write_date(self, json_file):
        json_dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": json_file})
        now = datetime.datetime.now()
        data = {"date": now}
        json_dn.write(data)
        read_data = json_dn.read()
        assert read_data["date"] == now

    def test_write_enum(self, json_file):
        json_dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": json_file})
        data = [MyEnum.A, MyEnum.B, MyEnum.C]
        json_dn.write(data)
        read_data = json_dn.read()
        assert read_data == [MyEnum.A, MyEnum.B, MyEnum.C]

    def test_write_dataclass(self, json_file):
        json_dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": json_file})
        json_dn.write(CustomDataclass(integer=1, string="foo"))
        read_data = json_dn.read()
        assert read_data.integer == 1
        assert read_data.string == "foo"

    def test_write_custom_encoder(self, json_file):
        json_dn = JSONDataNode(
            "foo", Scope.SCENARIO, properties={"default_path": json_file, "encoder": MyCustomEncoder}
        )
        data = [MyCustomObject("1", 1, "abc"), 100]
        json_dn.write(data)
        read_data = json_dn.read()
        assert read_data[0]["__type__"] == "MyCustomObject"
        assert read_data[0]["id"] == "1"
        assert read_data[0]["integer"] == 1
        assert read_data[0]["text"] == "abc"
        assert read_data[1] == 100

    def test_read_write_custom_encoder_decoder(self, json_file):
        json_dn = JSONDataNode(
            "foo",
            Scope.SCENARIO,
            properties={"default_path": json_file, "encoder": MyCustomEncoder, "decoder": MyCustomDecoder},
        )
        data = [MyCustomObject("1", 1, "abc"), 100]
        json_dn.write(data)
        read_data = json_dn.read()
        assert isinstance(read_data[0], MyCustomObject)
        assert read_data[0].id == "1"
        assert read_data[0].integer == 1
        assert read_data[0].text == "abc"
        assert read_data[1] == 100

    def test_filter(self, json_file):
        json_dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": json_file})
        json_dn.write(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
                {"KWARGS_KEY": "KWARGS_VALUE"},
            ]
        )

        assert len(json_dn.filter(("foo", 1, Operator.EQUAL))) == 3
        assert len(json_dn.filter(("foo", 1, Operator.NOT_EQUAL))) == 3
        assert len(json_dn.filter(("bar", 2, Operator.EQUAL))) == 3
        assert len(json_dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)) == 4

        assert json_dn[0] == {"foo": 1, "bar": 1}
        assert json_dn[2] == {"foo": 1}
        assert json_dn[:2] == [{"foo": 1, "bar": 1}, {"foo": 1, "bar": 2}]

    @pytest.mark.parametrize(
        ["properties", "exists"],
        [
            ({}, False),
            ({"default_data": {"foo": "bar"}}, True),
        ],
    )
    def test_create_with_default_data(self, properties, exists):
        dn = JSONDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)
        assert os.path.exists(dn.path) is exists

    def test_set_path(self):
        dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": "foo.json"})
        assert dn.path == "foo.json"
        dn.path = "bar.json"
        assert dn.path == "bar.json"

    def test_read_write_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_dict.json")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.json")
        dn = JSONDataNode("foo", Scope.SCENARIO, properties={"default_path": path})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write({"other": "stuff"})
        assert dn.read() == {"other": "stuff"}

    def test_get_system_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.json"))
        pd.DataFrame([]).to_json(temp_file_path)
        dn = JSONDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path})

        dn.write([1, 2, 3])
        previous_edit_date = dn.last_edit_date

        sleep(0.1)

        pd.DataFrame([4, 5, 6]).to_json(temp_file_path)
        new_edit_date = datetime.datetime.fromtimestamp(os.path.getmtime(temp_file_path))

        assert previous_edit_date < dn.last_edit_date
        assert new_edit_date == dn.last_edit_date

        sleep(0.1)

        dn.write([1, 2, 3])
        assert new_edit_date < dn.last_edit_date
        os.unlink(temp_file_path)
