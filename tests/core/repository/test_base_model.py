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
import enum
import json

import pytest

from taipy.core._repository._base_taipy_model import _BaseModel, _Encoder


class SampleEnum(enum.Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"


@dataclasses.dataclass
class SampleModel(_BaseModel):
    attr1: int
    attr2: str
    attr3: SampleEnum


@pytest.fixture
def sample_model():
    return SampleModel(attr1=1, attr2="test", attr3=SampleEnum.VALUE1)


def test_iter(sample_model):
    items = dict(sample_model)
    expected_items = {"attr1": 1, "attr2": "test", "attr3": SampleEnum.VALUE1}
    assert items == expected_items


def test_to_dict(sample_model):
    model_dict = sample_model.to_dict()
    expected_dict = {"attr1": 1, "attr2": "test", "attr3": repr(SampleEnum.VALUE1)}
    assert model_dict == expected_dict


def test_serialize_attribute(sample_model):
    serialized = _BaseModel._serialize_attribute(sample_model.attr2)
    expected_serialized = json.dumps(sample_model.attr2, ensure_ascii=False, cls=_Encoder)
    assert serialized == expected_serialized


def test_deserialize_attribute(sample_model):
    serialized = json.dumps(sample_model.attr2, ensure_ascii=False, cls=_Encoder)
    deserialized = _BaseModel._deserialize_attribute(serialized)
    assert deserialized == sample_model.attr2
