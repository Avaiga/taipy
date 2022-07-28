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

import datetime
import json
import os
import pathlib
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pytest

from src.taipy.core.common.alias import DataNodeId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.json import JSONDataNode
from src.taipy.core.exceptions.exceptions import MissingRequiredProperty, NoData
from taipy.config.config import Config
from taipy.config.data_node.scope import Scope
from taipy.config.exceptions.exceptions import InvalidConfigurationId


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
        dn = JSONDataNode("foo_bar", Scope.PIPELINE, name="super name", properties={"default_path": path})
        assert isinstance(dn, JSONDataNode)
        assert dn.storage_type() == "json"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.parent_id is None
        assert dn.last_edition_date is None
        assert dn.job_ids == []
        assert not dn.is_ready_for_reading
        assert dn.path == path

        with pytest.raises(InvalidConfigurationId):
            dn = JSONDataNode(
                "foo bar", Scope.PIPELINE, name="super name", properties={"default_path": path, "has_header": False}
            )

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

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            JSONDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            JSONDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={})

    def test_read_non_existing_json(self):
        not_existing_json = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": "WRONG.json"})
        with pytest.raises(NoData):
            assert not_existing_json.read() is None
            not_existing_json.read_or_raise()

    def test_read(self):
        path_1 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_list.json")
        dn_1 = JSONDataNode("bar", Scope.PIPELINE, properties={"default_path": path_1})
        data_1 = dn_1.read()
        assert isinstance(data_1, list)
        assert len(data_1) == 4

        path_2 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_dict.json")
        dn_2 = JSONDataNode("bar", Scope.PIPELINE, properties={"default_path": path_2})
        data_2 = dn_2.read()
        assert isinstance(data_2, dict)
        assert data_2["id"] == "1"

        path_3 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_int.json")
        dn_3 = JSONDataNode("bar", Scope.PIPELINE, properties={"default_path": path_3})
        data_3 = dn_3.read()
        assert isinstance(data_3, int)
        assert data_3 == 1

        path_4 = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/json/example_null.json")
        dn_4 = JSONDataNode("bar", Scope.PIPELINE, properties={"default_path": path_4})
        data_4 = dn_4.read()
        assert data_4 is None

    def test_read_invalid_json(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/invalid.json.txt")
        dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": path})
        with pytest.raises(ValueError):
            dn.read()

    def test_write(self, json_file):
        json_dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": json_file})
        data = {"a": 1, "b": 2, "c": 3}
        json_dn.write(data)
        assert np.array_equal(json_dn.read(), data)

    def test_write_non_serializable(self, json_file):
        json_dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": json_file})
        data = {"a": 1, "b": json_dn}
        with pytest.raises(TypeError):
            json_dn.write(data)

    def test_write_date(self, json_file):
        json_dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": json_file})
        now = datetime.datetime.now()
        now_str = now.isoformat()
        data = {"date": now}
        json_dn.write(data)
        read_data = json_dn.read()
        assert read_data["date"] == now_str

    def test_write_enum(self, json_file):
        class MyEnum(Enum):
            A = 1
            B = 2
            C = 3

        json_dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": json_file})
        data = [MyEnum.A, MyEnum.B, MyEnum.C]
        json_dn.write(data)
        read_data = json_dn.read()
        assert read_data == [1, 2, 3]

    def test_write_dataclass(self, json_file):
        @dataclass
        class CustomDataclass:
            integer: int
            string: str

        json_dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": json_file})
        json_dn.write(CustomDataclass(integer=1, string="foo"))
        read_data = json_dn.read()
        assert read_data["integer"] == 1
        assert read_data["string"] == "foo"

    def test_write_custom_encoder(self, json_file):
        json_dn = JSONDataNode(
            "foo", Scope.PIPELINE, properties={"default_path": json_file, "encoder": MyCustomEncoder}
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
            Scope.PIPELINE,
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

    def test_set_path(self):
        dn = JSONDataNode("foo", Scope.PIPELINE, properties={"default_path": "foo.json"})
        assert dn.path == "foo.json"
        dn.path = "bar.json"
        assert dn.path == "bar.json"

    def test_raise_error_when_path_not_exist(self):
        with pytest.raises(MissingRequiredProperty):
            JSONDataNode("foo", Scope.PIPELINE)
