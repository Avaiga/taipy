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

from taipy.gui import Gui, State
from taipy.testing.gui.testing_state import TestingState


def test_read_attr():
    gui = Gui("")
    ts = TestingState(gui, a = 1)
    assert ts is not None
    assert ts.get_gui() is gui
    assert ts.a == 1
    assert ts.b is None

def test_read_context():
    ts = TestingState(Gui(""), a = 1)
    assert ts is not None
    assert ts["b"] is not None
    assert ts["b"].a == 1

def test_write_attr():
    ts = TestingState(Gui(""), a = 1)
    assert ts is not None
    ts.a = 2
    assert ts.a == 2
    ts.b = 3
    assert ts.b == 3

def test_write_context():
    ts = TestingState(Gui(""), a = 1)
    assert ts is not None
    ts["page"].a = 2
    assert ts["page"].a == 2
    ts["page"].b = 3
    assert ts["page"].b == 3

def test_callback():
    def on_action(state: State):
        state.assign("a", 2)

    ts = TestingState(Gui(""), a = 1)
    on_action(ts)
    assert ts.a == 2
