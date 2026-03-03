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


from taipy.gui.utils.patch import _patch_value


def test_patch_change_dict():
    obj = {"a": {"b": {"c": 1}}}
    _patch_value(obj, {"a": {"b": {"c": 2}}})
    assert obj.get("a").get("b").get("c") == 2  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_add_to_dict():
    obj = {"a": {"b": {"c": 1}}}
    _patch_value(obj, {"a": {"b": {"d": 2}}})
    assert obj.get("a").get("b").get("c") == 1  # pyright: ignore[reportOptionalMemberAccess]
    assert obj.get("a").get("b").get("d") == 2  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_update_scalar_in_dict():
    obj = {"a": {"b": {"c": None}}}
    _patch_value(obj, {"a": {"b": {"c": 2}}})
    assert obj.get("a").get("b").get("c") == 2  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_remove_dict():
    obj = {"a": {"b": {"c": 1}}}
    _patch_value(obj, None, {"a": {"b": {"c": None}}})
    assert obj.get("a").get("b").get("c", "") == ""  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_change_list():
    obj = {"a": {"b": {"c": [0, 1, 2]}}}
    _patch_value(obj, {"a": {"b": {"c": {2: 4}}}})
    assert obj.get("a").get("b").get("c") == [0, 1, 4]  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_change_list_by_list():
    obj = {"a": {"b": {"c": [0, 1, 2]}}}
    _patch_value(obj, {"a": {"b": {"c": {1: [-1, -2, -3]}}}})
    assert obj.get("a").get("b").get("c") == [0, -1, -2, -3]  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_remove_list():
    obj = {"a": {"b": {"c": [0, 1, 2]}}}
    _patch_value(obj, None, {"a": {"b": {"c": {1: None}}}})
    assert obj.get("a").get("b").get("c", "") == [0, 2]  # pyright: ignore[reportOptionalMemberAccess]


def test_patch_change_whole_list():
    obj = {"a": {"b": {"c": [0, 2, 4]}}}
    _patch_value(obj, {"a": {"b": {"c": [1, 3, 5]}}})
    assert obj.get("a").get("b").get("c") == [1, 3, 5]  # pyright: ignore[reportOptionalMemberAccess]


def test_update_object_in_list():
    obj = {"a": {"b": [{"c": 1}, {"c": 2}, {"c": 3}]}}
    _patch_value(obj, {"a": {"b": {2: {"c": -1}}}})
    assert obj.get("a").get("b", [])[2].get("c") == -1  # pyright: ignore[reportOptionalMemberAccess]
    assert obj.get("a").get("b", [])[0].get("c") == 1  # pyright: ignore[reportOptionalMemberAccess]


def test_update_list_of_object():
    obj = {"a": {"b": [{"c": 1}, {"c": 2, "d": 3}, {"c": 4}]}}
    _patch_value(obj, {"a": {"b": {1: [{"c": -1}]}}})
    assert obj.get("a").get("b", [])[1].get("c") == -1  # pyright: ignore[reportOptionalMemberAccess]
    assert obj.get("a").get("b", [])[1].get("d") == 3  # pyright: ignore[reportOptionalMemberAccess]


def test_insert_list():
    obj = {"a": {"b": [0, 1, 2, 3]}}
    _patch_value(obj, {"a": {"b": {-1: [4, 5]}}})
    assert obj.get("a").get("b") == [4, 5, 0, 1, 2, 3]  # pyright: ignore[reportOptionalMemberAccess]

    obj2 = {"a": {"b": [0, 1, 2, 3]}}
    _patch_value(obj2, {"a": {"b": {-3: [4, 5]}}})
    assert obj2.get("a").get("b") == [0, 1, 4, 5, 2, 3]  # pyright: ignore[reportOptionalMemberAccess]


def test_update_empty_list():
    obj = {"a": {"b": []}}
    _patch_value(obj, {"a": {"b": {0: 1}}})
    assert obj.get("a").get("b", [])[0] == 1  # pyright: ignore[reportOptionalMemberAccess]
    assert len(obj.get("a").get("b", [])) == 1  # pyright: ignore[reportOptionalMemberAccess]

    obj2 = {"a": {"b": []}}
    _patch_value(obj2, {"a": {"b": {0: [1, 2]}}})
    assert obj2.get("a").get("b", [])[0] == 1  # pyright: ignore[reportOptionalMemberAccess]
    assert len(obj2.get("a").get("b", [])) == 2  # pyright: ignore[reportOptionalMemberAccess]


def test_update_empty_root_dict():
    obj = {}
    _patch_value(obj, {"a": {"b": {"c": 1}}})
    assert obj.get("a").get("b").get("c") == 1  # pyright: ignore[reportOptionalMemberAccess]


def test_update_empty_root_list():
    obj = []
    _patch_value(obj, {0: {"a": 1}})
    assert obj[0].get("a") == 1  # pyright: ignore[reportOptionalMemberAccess]


def test_update_list_of_list():
    obj = [[1, 2, 3], [4, 5, 6]]
    _patch_value(obj, {0: [[7, 8, 9]]})  # pyright: ignore[reportOptionalMemberAccess]
    assert obj[0] == [7, 8, 9]  # pyright: ignore[reportOptionalMemberAccess]
    assert obj[1] == [4, 5, 6]  # pyright: ignore[reportOptionalMemberAccess]
    assert len(obj) == 2  # pyright: ignore[reportOptionalMemberAccess]

    _patch_value(obj, {0: [[]]})
    assert len(obj[0]) == 0  # pyright: ignore[reportOptionalMemberAccess]
    assert obj[1] == [4, 5, 6]  # pyright: ignore[reportOptionalMemberAccess]
    assert len(obj) == 2  # pyright: ignore[reportOptionalMemberAccess]
