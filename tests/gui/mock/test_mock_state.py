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

from unittest.mock import Mock

from taipy.gui import Gui, State
from taipy.gui.mock.mock_state import MockState
from taipy.gui.utils import _MapDict


def test_gui():
    gui = Gui("")
    ms = MockState(gui)
    assert ms.get_gui() is gui
    assert ms._gui is gui


def test_read_attr():
    gui = Gui("")
    ms = MockState(gui, a=1)
    assert ms is not None
    assert ms.a == 1
    assert ms.b is None


def test_read_context():
    ms = MockState(Gui(""), a=1)
    assert ms["b"] is not None
    assert ms["b"].a == 1


def test_write_attr():
    ms = MockState(Gui(""), a=1)
    ms.a = 2
    assert ms.a == 2
    ms.b = 3
    assert ms.b == 3
    ms.a += 1
    assert ms.a == 3

def test_dict():
    ms = MockState(Gui(""))
    a_dict = {"a": 1}
    ms.d = a_dict
    assert isinstance(ms.d, _MapDict)
    assert ms.d._dict is a_dict


def test_write_context():
    ms = MockState(Gui(""), a=1)
    ms["page"].a = 2
    assert ms["page"].a == 2
    ms["page"].b = 3
    assert ms["page"].b == 3

def test_assign():
    ms = MockState(Gui(""), a=1)
    ms.assign("a", 2)
    assert ms.a == 2
    ms.assign("b", 1)
    assert ms.b == 1

def test_refresh():
    ms = MockState(Gui(""), a=1)
    ms.refresh("a")
    assert ms.a == 1
    ms.a = 2
    ms.refresh("a")
    assert ms.a == 2

def test_context_manager():
    with MockState(Gui(""), a=1) as ms:
        assert ms is not None
        ms.a = 2
    assert ms.a == 2

def test_broadcast():
    ms = MockState(Gui(""), a=1)
    ms.broadcast("a", 2)

def test_set_favicon():
    gui = Gui("")
    gui.set_favicon = Mock()
    ms = MockState(gui, a=1)
    ms.set_favicon("a_path")
    gui.set_favicon.assert_called_once()

def test_callback():
    def on_action(state: State):
        state.assign("a", 2)

    ms = MockState(Gui(""), a=1)
    on_action(ms)
    assert ms.a == 2

def test_false():
    ms = MockState(Gui(""), a=False)
    assert ms.a is False
