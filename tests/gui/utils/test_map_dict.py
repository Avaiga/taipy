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

import inspect

import pytest

from taipy.gui.gui import Gui
from taipy.gui.utils import _MapDict


def test_map_dict():
    d = {"a": 1, "b": 2, "c": 3}
    md = _MapDict(d)
    md_copy = _MapDict(d).copy()
    assert len(md) == 3
    assert md.__getitem__("a") == d["a"]
    md.__setitem__("a", 4)
    assert md.__getitem__("a") == 4
    assert d["a"] == 4
    v1 = d["b"]
    v2 = md.pop("b")
    assert v1 == v2
    assert "b" not in d.keys()
    assert "c" in md
    assert len(md) == 2
    v1 = d["c"]
    v2 = md.popitem()
    assert v2 == ("c", v1)
    assert len(md) == 1
    md.clear()
    assert len(md) == 0
    assert len(d) == 0
    assert len(md_copy) == 3
    v1 = ""
    for k in md_copy:
        v1 += k
    assert v1 == "abc"
    v1 = ""
    for k in md_copy.keys():
        v1 += k
    assert v1 == "abc"
    v1 = ""
    for k in md_copy.__reversed__():
        v1 += k
    assert v1 == "cba"
    v1 = 0
    for k in md_copy.values():
        v1 += k
    assert v1 == 6  # 1+2+3
    v1 = md_copy.setdefault("a", 5)
    assert v1 == 1
    v1 = md_copy.setdefault("d", 5)
    assert v1 == 5

    try:
        md = _MapDict("not_a_dict")
        assert False
    except Exception:
        assert True
    pass


def test_map_dict_update():
    update_values = {}

    def update(k, v):
        update_values[0] = k
        update_values[1] = v
        pass

    d = {"a": 1, "b": "2"}
    md = _MapDict(d, update)
    md.__setitem__("a", 3)
    assert update_values[0] == "a"
    assert update_values[1] == 3
    pass


def test_map_dict_update_full_dictionary_1():
    values = {"a": 1, "b": 2}
    update_values = {"a": 3, "b": 5}
    md = _MapDict(values)
    assert md["a"] == 1
    assert md["b"] == 2
    md.update(update_values)
    assert md["a"] == 3
    assert md["b"] == 5


def test_map_dict_update_full_dictionary_2():
    temp_values = {}

    def update(k, v):
        temp_values[k] = v

    values = {"a": 1, "b": 2}
    update_values = {"a": 3, "b": 5}
    md = _MapDict(values, update)
    assert md["a"] == 1
    assert md["b"] == 2
    md.update(update_values)
    assert temp_values["a"] == 3
    assert temp_values["b"] == 5


def test_map_dict_set(gui: Gui, test_client):
    d = {"a": 1}  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.run(run_server=False, single_client=True)
    with gui.get_flask_app().app_context():
        assert isinstance(gui._Gui__state.d, _MapDict)
        gui._Gui__state.d = {"b": 2}
        assert isinstance(gui._Gui__state.d, _MapDict)
        assert len(gui._Gui__state.d) == 1
        assert gui._Gui__state.d.get("a", None) is None
        assert gui._Gui__state.d.get("b", None) == 2


def test_map_dict_items():
    def update(k, v):
        pass

    values = {"a": 1, "b": {"c": "list c"}}
    md = _MapDict(values)
    mdu = _MapDict(values, update)
    assert md["a"] == 1
    assert isinstance(md["b"], _MapDict)
    assert isinstance(mdu["b"], _MapDict)
    assert md["b"]["c"] == "list c"
    assert mdu["b"]["c"] == "list c"
    del md["a"]
    with pytest.raises(KeyError):
        md["e"]
    setattr(md, "a", 1)
    assert md["a"] == 1
