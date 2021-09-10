import json

from taipy.data.data_source.csv import CSVDataSourceEntity
from taipy.data.data_source.embedded import EmbeddedDataSourceEntity
from taipy.data.data_source.models import Scope
from taipy.exceptions import InvalidDataSourceType


class DataSource:
    __ENTITY_MAP = {"csv": CSVDataSourceEntity, "embedded": EmbeddedDataSourceEntity}

    @classmethod
    def __get_entity(cls, type: str):
        ds_entity = cls.__ENTITY_MAP.get(type)
        if ds_entity is None:
            raise InvalidDataSourceType(f"{type} is not a valid Data Source Type")
        return ds_entity

    def __new__(cls, unique_name: str, type: str, **kwargs):
        ds_entity = cls.__get_entity(type)
        return ds_entity(name=unique_name, scope=Scope.PIPELINE, properties=kwargs)

    @classmethod
    def from_json(cls, json_path):
        with open(json_path) as j:
            ds_dict = json.load(j)

        return cls.__get_entity(ds_dict.get("type")).from_json(ds_dict)

    @classmethod
    def to_json(cls):
        return vars(cls)


if __name__ == "__main__":
    ds = DataSource(unique_name="foo", type="csv", path="foo", has_header=True)
    print(ds.to_json())

    ds2 = DataSource.from_json(json_path="/Users/qwerty/ds_descriptor.json")
    print(ds2.to_json())
    assert isinstance(ds2, CSVDataSourceEntity)
