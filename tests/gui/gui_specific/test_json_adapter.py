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
from datetime import timedelta
from pathlib import Path

import numpy

from taipy.gui import Icon
from taipy.gui._renderers.json import JsonAdapter, _TaipyJsonEncoder
from taipy.gui.utils import _DoNotUpdate, _TaipyNumber


def test_default_adapter():
    var = 123
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == json.dumps(var)

    var = Icon("image.png", "Text")
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == json.dumps({"path": "image.png", "text": "Text"})

    var = _TaipyNumber(123, "number")
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == "123.0"

    var = Path("a", "b")
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    json_string = json_string.replace("\\\\", "/")
    assert json_string == '"a/b"'

    var = timedelta(1.5)
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == '"1 day, 12:00:00"'

    var = numpy.int32(123)
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == "123"

    var = _DoNotUpdate()
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == "null"


def test_adapter_unknown(helpers):
    class TestClass:
        def __init__(self, value: str):
            self._value = value

    var = TestClass("test")
    with warnings.catch_warnings(record=True) as records:
        json_string = json.dumps(var, cls=_TaipyJsonEncoder)
        assert json_string == "null"
        warns = helpers.get_taipy_warnings(records)
        assert len(warns) == 1
        assert "TestClass is not JSON serializable" in str(warns[0].message)


def test_custom_adapter():
    class TestClass:
        def __init__(self, value: str):
            self._value = TestClass.change_string(value)

        @staticmethod
        def change_string(s: str) -> str:
            return s[::-1]

    class TestAdapter(JsonAdapter):
        def to_jsonable(self, o) -> t.Optional[t.Any]:
            if isinstance(o, TestClass):
                return o._value
            return None

    TestAdapter().register()

    s = "abc"
    var = TestClass(s)
    json_string = json.dumps(var, cls=_TaipyJsonEncoder)
    assert json_string == json.dumps(TestClass.change_string(s))
