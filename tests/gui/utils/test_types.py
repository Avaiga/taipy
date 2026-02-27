# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


import json
import typing as t
import warnings

import pytest

from taipy.gui.utils._map_dict import _MapDict
from taipy.gui.utils.date import _string_to_date
from taipy.gui.utils.types import (
    JsonableProperty,
    JsonProperty,
    _TaipyBool,
    _TaipyData,
    _TaipyDate,
    _TaipyDateRange,
    _TaipyDict,
    _TaipyNumber,
    _TaipyTime,
    _TaipyToJson,
    _TaipyToJsonable,
)


def test_taipy_data():
    tb = _TaipyData("value", "hash")
    assert tb.get() == "value"
    assert tb.get_name() == "hash"
    tb.set("a value")
    assert tb.get() == "a value"
    assert tb.get_hash() == "_TpD"


def test_taipy_bool():
    assert _TaipyBool(0, "v").get() is False
    assert _TaipyBool(1, "v").get() is True
    assert _TaipyBool(False, "v").get() is False
    assert _TaipyBool(True, "v").get() is True
    assert _TaipyBool("", "v").get() is False
    assert _TaipyBool("hey", "v").get() is True
    assert _TaipyBool([], "v").get() is False
    assert _TaipyBool(["an item"], "v").get() is True


def test_taipy_number():
    with pytest.raises(TypeError):
        _TaipyNumber("a string", "x").get()
    with warnings.catch_warnings(record=True):
        _TaipyNumber("a string", "x").cast_value("a string")
    _TaipyNumber(0, "x").cast_value(0)


def test_taipy_date():
    assert _TaipyDate(_string_to_date("2022-03-03 00:00:00 UTC"), "x").get() == "2022-03-03T00:00:00+00:00"
    assert _TaipyDate("2022-03-03 00:00:00 UTC", "x").get() == "2022-03-03 00:00:00 UTC"
    assert _TaipyDate(None, "x").get() is None
    _TaipyDate("", "x").cast_value("2022-03-03 00:00:00 UTC")
    _TaipyDate("", "x").cast_value(_string_to_date("2022-03-03 00:00:00 UTC"))


def test_taipy_date_range():
    assert _TaipyDateRange([_string_to_date("2022-03-03 00:00:00 UTC")], "x").get() == ["2022-03-03T00:00:00+00:00"]
    assert _TaipyDateRange(["2022-03-03 00:00:00 UTC"], "x").get() == ["2022-03-03 00:00:00 UTC"]
    assert _TaipyDate(None, "x").get() is None
    _TaipyDate("", "x").cast_value(["2022-03-03 00:00:00 UTC"])
    _TaipyDate("", "x").cast_value([_string_to_date("2022-03-03 00:00:00 UTC")])


def test_taipy_dict():
    assert _TaipyDict({"key": "value"}, "x").get() == '{"key": "value"}'
    assert _TaipyDict(None, "x").get() == "null"


def test_taipy_time():
    assert _TaipyTime(_string_to_date("2022-03-03T00:00:00"), "x").get() == "2022-03-03T00:00:00"
    assert _TaipyTime("2022-03-03T00:00:00", "x").get() == "2022-03-03T00:00:00"
    assert _TaipyTime(None, "x").get() is None
    _TaipyTime("", "x").cast_value("2022-03-03T00:00:00")
    _TaipyTime("", "x").cast_value(_string_to_date("2022-03-03T00:00:00"))


TEST_DICT = {"key": "value"}


def test_taipy_to_json():
    json_value = json.dumps(TEST_DICT)

    class TestJson(JsonProperty):
        def to_json(self) -> str:
            return json_value

    tb = _TaipyToJson(TestJson(), "hash")
    assert tb.get() == json_value
    assert tb.get_name() == "hash"
    assert tb.get_hash() == "_TpTj"

    class TestJsonable(JsonableProperty):
        def to_jsonable(self):
            return {"key": "value"}

    tb = _TaipyToJsonable(TestJsonable(), "hash")
    assert tb.get() == {"key": "value"}
    assert tb.get_name() == "hash"
    assert tb.get_hash() == "_TpJ"

    class PseudoPlotlyFigure:
        def to_json(self):
            return '{"data": [], "layout": {}}'

    tb = _TaipyToJson(PseudoPlotlyFigure(), "hash")
    assert tb.get() == '{"data": [], "layout": {}}'

    assert _TaipyToJson(None, "hash").get() is None


def test_taipy_to_jsonable_with_to_dict():
    class TestToDict:
        def to_dict(self):
            return {"key": "value"}

    tb = _TaipyToJsonable(TestToDict(), "hash")
    assert tb.get() == {"key": "value"}
    assert tb.get_name() == "hash"
    assert tb.get_hash() == "_TpJ"


def test_taipy_to_jsonable_with_dict():
    tb = _TaipyToJsonable({}, "hash")
    assert tb.get() == {}

    tb = _TaipyToJsonable(TEST_DICT, "hash")
    assert tb.get() == TEST_DICT


def test_taipy_to_jsonable_with_MapDict():
    tb = _TaipyToJsonable(_MapDict({}), "hash")
    assert tb.get() == {}

    tb = _TaipyToJsonable(_MapDict(TEST_DICT), "hash")
    assert tb.get() == TEST_DICT


class TypedDictCustomClass(t.TypedDict):
    name: str
    year: int


def test_taipy_to_jsonable_with_typed_dict():
    tb = _TaipyToJsonable(TypedDictCustomClass(name="name", year=1928), "hash")
    assert tb.get() == {"name": "name", "year": 1928}


def test_taipy_to_jsonable_with_list():
    tb = _TaipyToJsonable([], "hash")
    assert tb.get() == []

    tb = _TaipyToJsonable(["key", "value"], "hash")
    assert tb.get() == ["key", "value"]


def test_taipy_to_jsonable_with_tuple():
    tb = _TaipyToJsonable((), "hash")
    assert tb.get() == ()

    tb = _TaipyToJsonable(("key", "value"), "hash")
    assert tb.get() == ("key", "value")


def test_taipy_to_jsonable_with_string():
    tb = _TaipyToJsonable("", "hash")
    assert tb.get() == ""

    tb = _TaipyToJsonable("a string", "hash")
    assert tb.get() == "a string"


def test_taipy_to_jsonable_with_non_serializable():
    class NonSerializable:
        pass

    with warnings.catch_warnings(record=True) as w:
        tb = _TaipyToJsonable(NonSerializable(), "hash")
        assert tb.get() is None
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert "'hash.to_jsonable()' must be defined." in str(w[-1].message)


def test_taipy_to_jsonable_with_exception_to_jsonable():
    class ExceptionInToJsonable:
        def to_jsonable(self):
            raise Exception("Exception in to_jsonable")

    with warnings.catch_warnings(record=True) as w:
        tb = _TaipyToJsonable(ExceptionInToJsonable(), "hash")
        assert tb.get() is None
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert "Issue while serializing" in str(w[-1].message)


def test_taipy_to_json_with_set():
    tb = _TaipyToJsonable(set(), "hash")
    assert tb.get() == []

    tb = _TaipyToJsonable(("key", "value"), "hash")
    assert tb.get() == ("key", "value")
