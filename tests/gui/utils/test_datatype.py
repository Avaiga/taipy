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


from taipy.gui.utils._map_dict import _MapDict
from taipy.gui.utils.datatype import _get_data_type


def test_datatype_str():
    ret = _get_data_type("a string")
    assert ret == "str"


def test_datatype_dict():
    a_dict = {"a": "b", "c": "d"}
    ret = _get_data_type(a_dict)
    assert ret == "dict"
    ret = _get_data_type(_MapDict(a_dict))
    assert ret == "dict"


def test_datatype_bool():
    ret = _get_data_type(True)
    assert ret == "bool"


def test_datatype_int():
    ret = _get_data_type(42)
    assert ret == "int"


def test_datatype_float():
    ret = _get_data_type(3.14)
    assert ret == "float"


def test_datatype_none():
    ret = _get_data_type(None)
    assert ret == "NoneType"
