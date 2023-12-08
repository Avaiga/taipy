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


from dataclasses import dataclass
from datetime import datetime
from unittest.mock import patch

import mongomock
import pymongo
import pytest
from bson import ObjectId
from bson.errors import InvalidDocument

from taipy.config.common.scope import Scope
from taipy.core import MongoDefaultDocument
from taipy.core.common._mongo_connector import _connect_mongodb
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.mongo import MongoCollectionDataNode
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.exceptions.exceptions import InvalidCustomDocument, MissingRequiredProperty


@pytest.fixture(scope="function", autouse=True)
def clear_mongo_connection_cache():
    _connect_mongodb.cache_clear()


@dataclass
class CustomObjectWithoutArgs:
    def __init__(self, foo=None, bar=None):
        self.foo = foo
        self.bar = bar


class CustomObjectWithCustomEncoder:
    def __init__(self, _id=None, integer=None, text=None, time=None):
        self.id = _id
        self.integer = integer
        self.text = text
        self.time = time

    def encode(self):
        return {"_id": self.id, "integer": self.integer, "text": self.text, "time": self.time.isoformat()}


class CustomObjectWithCustomEncoderDecoder(CustomObjectWithCustomEncoder):
    @classmethod
    def decode(cls, data):
        return cls(data["_id"], data["integer"], data["text"], datetime.fromisoformat(data["time"]))


class TestMongoCollectionDataNode:
    __properties = [
        {
            "db_username": "",
            "db_password": "",
            "db_name": "taipy",
            "collection_name": "foo",
            "custom_document": MongoDefaultDocument,
            "db_extra_args": {
                "ssl": "true",
                "retrywrites": "false",
                "maxIdleTimeMS": "120000",
            },
        }
    ]

    @pytest.mark.parametrize("properties", __properties)
    def test_create(self, properties):
        mongo_dn = MongoCollectionDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties=properties,
        )
        assert isinstance(mongo_dn, MongoCollectionDataNode)
        assert mongo_dn.storage_type() == "mongo_collection"
        assert mongo_dn.config_id == "foo_bar"
        assert mongo_dn.scope == Scope.SCENARIO
        assert mongo_dn.id is not None
        assert mongo_dn.owner_id is None
        assert mongo_dn.job_ids == []
        assert mongo_dn.is_ready_for_reading
        assert mongo_dn.custom_document == MongoDefaultDocument

    @pytest.mark.parametrize("properties", __properties)
    def test_get_user_properties(self, properties):
        custom_properties = properties.copy()
        custom_properties["foo"] = "bar"
        mongo_dn = MongoCollectionDataNode(
            "foo_bar",
            Scope.SCENARIO,
            properties=custom_properties,
        )
        assert mongo_dn._get_user_properties() == {"foo": "bar"}

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
            MongoCollectionDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            MongoCollectionDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties=properties)

    @pytest.mark.parametrize("properties", __properties)
    def test_raise_error_invalid_custom_document(self, properties):
        custom_properties = properties.copy()
        custom_properties["custom_document"] = "foo"
        with pytest.raises(InvalidCustomDocument):
            MongoCollectionDataNode(
                "foo",
                Scope.SCENARIO,
                properties=custom_properties,
            )

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_read(self, properties):
        mock_client = pymongo.MongoClient("localhost")
        mock_client[properties["db_name"]][properties["collection_name"]].insert_many(
            [
                {"foo": "baz", "bar": "qux"},
                {"foo": "quux", "bar": "quuz"},
                {"foo": "corge"},
                {"bar": "grault"},
                {"KWARGS_KEY": "KWARGS_VALUE"},
                {},
            ]
        )

        mongo_dn = MongoCollectionDataNode(
            "foo",
            Scope.SCENARIO,
            properties=properties,
        )

        data = mongo_dn.read()

        assert isinstance(data, list)
        assert isinstance(data[0], MongoDefaultDocument)
        assert isinstance(data[1], MongoDefaultDocument)
        assert isinstance(data[2], MongoDefaultDocument)
        assert isinstance(data[3], MongoDefaultDocument)
        assert isinstance(data[4], MongoDefaultDocument)
        assert isinstance(data[5], MongoDefaultDocument)

        assert isinstance(data[0]._id, ObjectId)
        assert data[0].foo == "baz"
        assert data[0].bar == "qux"
        assert isinstance(data[1]._id, ObjectId)
        assert data[1].foo == "quux"
        assert data[1].bar == "quuz"
        assert isinstance(data[2]._id, ObjectId)
        assert data[2].foo == "corge"
        assert isinstance(data[3]._id, ObjectId)
        assert data[3].bar == "grault"
        assert isinstance(data[4]._id, ObjectId)
        assert data[4].KWARGS_KEY == "KWARGS_VALUE"
        assert isinstance(data[5]._id, ObjectId)

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_read_empty_as(self, properties):
        mongo_dn = MongoCollectionDataNode(
            "foo",
            Scope.SCENARIO,
            properties=properties,
        )
        data = mongo_dn.read()
        assert isinstance(data, list)
        assert len(data) == 0

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    @pytest.mark.parametrize(
        "data",
        [
            ([{"foo": 1, "a": 2}, {"foo": 3, "bar": 4}]),
            ({"a": 1, "bar": 2}),
        ],
    )
    def test_read_wrong_object_properties_name(self, properties, data):
        custom_properties = properties.copy()
        custom_properties["custom_document"] = CustomObjectWithoutArgs
        mongo_dn = MongoCollectionDataNode(
            "foo",
            Scope.SCENARIO,
            properties=custom_properties,
        )
        mongo_dn.write(data)

        with pytest.raises(TypeError):
            data = mongo_dn.read()

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    @pytest.mark.parametrize(
        "data",
        [
            ([{"foo": 11, "bar": 22}, {"foo": 33, "bar": 44}]),
            ({"foz": 1, "baz": 2}),
        ],
    )
    def test_append(self, properties, data):
        mongo_dn = MongoCollectionDataNode("foo", Scope.SCENARIO, properties=properties)
        mongo_dn.append(data)

        original_data = [{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}]
        mongo_dn.write(original_data)

        mongo_dn.append(data)
        assert len(mongo_dn.read()) == len(data if isinstance(data, list) else [data]) + len(original_data)

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    @pytest.mark.parametrize(
        "data,written_data",
        [
            ([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}], [{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}]),
            ({"foo": 1, "bar": 2}, [{"foo": 1, "bar": 2}]),
        ],
    )
    def test_write(self, properties, data, written_data):
        mongo_dn = MongoCollectionDataNode("foo", Scope.SCENARIO, properties=properties)
        mongo_dn.write(data)

        read_objects = mongo_dn.read()

        for read_object, written_dict in zip(read_objects, written_data):
            assert isinstance(read_object._id, ObjectId)
            assert read_object.foo == written_dict["foo"]
            assert read_object.bar == written_dict["bar"]

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    @pytest.mark.parametrize(
        "data",
        [
            [],
        ],
    )
    def test_write_empty_list(self, properties, data):
        mongo_dn = MongoCollectionDataNode(
            "foo",
            Scope.SCENARIO,
            properties=properties,
        )
        mongo_dn.write(data)

        assert len(mongo_dn.read()) == 0

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_write_non_serializable(self, properties):
        mongo_dn = MongoCollectionDataNode("foo", Scope.SCENARIO, properties=properties)
        data = {"a": 1, "b": mongo_dn}
        with pytest.raises(InvalidDocument):
            mongo_dn.write(data)

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_write_custom_encoder(self, properties):
        custom_properties = properties.copy()
        custom_properties["custom_document"] = CustomObjectWithCustomEncoder
        mongo_dn = MongoCollectionDataNode("foo", Scope.SCENARIO, properties=custom_properties)
        data = [
            CustomObjectWithCustomEncoder("1", 1, "abc", datetime.now()),
            CustomObjectWithCustomEncoder("2", 2, "def", datetime.now()),
        ]
        mongo_dn.write(data)

        read_data = mongo_dn.read()

        assert isinstance(read_data[0], CustomObjectWithCustomEncoder)
        assert isinstance(read_data[1], CustomObjectWithCustomEncoder)
        assert read_data[0].id == "1"
        assert read_data[0].integer == 1
        assert read_data[0].text == "abc"
        assert isinstance(read_data[0].time, str)
        assert read_data[1].id == "2"
        assert read_data[1].integer == 2
        assert read_data[1].text == "def"
        assert isinstance(read_data[1].time, str)

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_write_custom_encoder_decoder(self, properties):
        custom_properties = properties.copy()
        custom_properties["custom_document"] = CustomObjectWithCustomEncoderDecoder
        mongo_dn = MongoCollectionDataNode("foo", Scope.SCENARIO, properties=custom_properties)
        data = [
            CustomObjectWithCustomEncoderDecoder("1", 1, "abc", datetime.now()),
            CustomObjectWithCustomEncoderDecoder("2", 2, "def", datetime.now()),
        ]
        mongo_dn.write(data)

        read_data = mongo_dn.read()

        assert isinstance(read_data[0], CustomObjectWithCustomEncoderDecoder)
        assert isinstance(read_data[1], CustomObjectWithCustomEncoderDecoder)
        assert read_data[0].id == "1"
        assert read_data[0].integer == 1
        assert read_data[0].text == "abc"
        assert isinstance(read_data[0].time, datetime)
        assert read_data[1].id == "2"
        assert read_data[1].integer == 2
        assert read_data[1].text == "def"
        assert isinstance(read_data[1].time, datetime)

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_filter(self, properties):
        mock_client = pymongo.MongoClient("localhost")
        mock_client[properties["db_name"]][properties["collection_name"]].insert_many(
            [
                {"foo": 1, "bar": 1},
                {"foo": 1, "bar": 2},
                {"foo": 1},
                {"foo": 2, "bar": 2},
                {"bar": 2},
                {"KWARGS_KEY": "KWARGS_VALUE"},
            ]
        )

        mongo_dn = MongoCollectionDataNode(
            "foo",
            Scope.SCENARIO,
            properties=properties,
        )

        assert len(mongo_dn.filter(("foo", 1, Operator.EQUAL))) == 3
        assert len(mongo_dn.filter(("foo", 1, Operator.NOT_EQUAL))) == 3
        assert len(mongo_dn.filter(("bar", 2, Operator.EQUAL))) == 3
        assert len(mongo_dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)) == 4

        assert mongo_dn["foo"] == [1, 1, 1, 2, None, None]
        assert mongo_dn["bar"] == [1, 2, None, 2, 2, None]
        assert [m.__dict__ for m in mongo_dn[:3]] == [m.__dict__ for m in mongo_dn.read()[:3]]
        assert mongo_dn[["foo", "bar"]] == [
            {"foo": 1, "bar": 1},
            {"foo": 1, "bar": 2},
            {"foo": 1},
            {"foo": 2, "bar": 2},
            {"bar": 2},
            {},
        ]

    @mongomock.patch(servers=(("localhost", 27017),))
    @pytest.mark.parametrize("properties", __properties)
    def test_filter_does_not_read_all_entities(self, properties):
        mongo_dn = MongoCollectionDataNode("foo", Scope.SCENARIO, properties=properties)

        # MongoCollectionDataNode.filter() should not call the MongoCollectionDataNode._read() method
        with patch.object(MongoCollectionDataNode, "_read") as read_mock:
            mongo_dn.filter(("foo", 1, Operator.EQUAL))
            mongo_dn.filter(("bar", 2, Operator.NOT_EQUAL))
            mongo_dn.filter([("bar", 1, Operator.EQUAL), ("bar", 2, Operator.EQUAL)], JoinOperator.OR)

            assert read_mock["_read"].call_count == 0
