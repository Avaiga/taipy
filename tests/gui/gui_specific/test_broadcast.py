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

import contextlib
import inspect

import pytest

from taipy.gui import Gui


@contextlib.contextmanager
def get_state(gui: Gui, state_id: str):
    with gui.get_flask_app().app_context():
        client_id = gui._bindings()._get_or_create_scope(state_id)[0]
        gui._Gui__set_client_id_in_context(client_id)  # type: ignore[attr-defined]
        yield gui._Gui__state  # type: ignore[attr-defined]

def test_multiple_scopes(gui: Gui):
    var = 1  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page("page1", "<|{var}|>")
    gui.run(run_server=False)
    with get_state(gui, "s1") as state1:
        assert state1.var == 1
    with get_state(gui, "s2") as state2:
        assert state2.var == 1
    with get_state(gui, "s1") as state1:
        state1.var = 2
        assert state1.var == 2
    with get_state(gui, "s2") as state2:
        assert state2.var == 1


def test_shared_variable(gui: Gui):
    var = 1  # noqa: F841
    s_var = 10  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page("test", "<|{var}|>")
    gui.add_shared_variable("s_var")
    gui.run(run_server=False)
    with get_state(gui, "s1") as state1:
        assert state1.var == 1
        assert state1.s_var == 10
        state1.var = 2
        state1.s_var = 20
        assert state1.var == 2
        assert state1.s_var == 20
    with get_state(gui, "s2") as state2:
        assert state2.var == 1
        assert state1.s_var == 20
    Gui._clear_shared_variable()


def test_broadcast_change(gui: Gui):
    # Bind test variables
    v1 = "none"  # noqa: F841
    v2 = 1  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page("test", " <|{v1}|><|{v2}|>")
    gui.run(run_server=False)
    s1, _ = gui._bindings()._get_or_create_scope("s1")
    s2, _ = gui._bindings()._get_or_create_scope("s2")
    gui.broadcast_change("v2", 2)
    with get_state(gui, s1) as state1:
        assert state1.v1 == "none"
        assert state1.v2 == 2
    with get_state(gui, s2) as state2:
        assert state2.v1 == "none"
        assert state2.v2 == 2

def test_broadcast_changes(gui: Gui):
    # Bind test variables
    v1 = "none"  # noqa: F841
    v2 = 1  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page("test", " <|{v1}|><|{v2}|>")
    gui.run(run_server=False)
    s1, _ = gui._bindings()._get_or_create_scope("s1")
    s2, _ = gui._bindings()._get_or_create_scope("s2")

    changes = { "v1": "some", "v2": 2}
    gui.broadcast_changes(changes)
    with get_state(gui, s1) as state1:
        assert state1.v1 == "some"
        assert state1.v2 == 2
    with get_state(gui, s2) as state2:
        assert state2.v1 == "some"
        assert state2.v2 == 2

    gui.broadcast_changes(v1="more", v2=3)
    with get_state(gui, s1) as state1:
        assert state1.v1 == "more"
        assert state1.v2 == 3
    with get_state(gui, s2) as state2:
        assert state2.v1 == "more"
        assert state2.v2 == 3

    gui.broadcast_changes({ "v1": "more yet"}, v2=4)
    with get_state(gui, s1) as state1:
        assert state1.v1 == "more yet"
        assert state1.v2 == 4
    with get_state(gui, s2) as state2:
        assert state2.v1 == "more yet"
        assert state2.v2 == 4


def test_broadcast_callback(gui: Gui):
    gui.run(run_server=False)

    res = gui.broadcast_callback(lambda _, t: t, ["Hello World"], "mine")
    assert isinstance(res, dict)
    assert not res

    gui._bindings()._get_or_create_scope("test scope")

    res = gui.broadcast_callback(lambda _, t: t, ["Hello World"], "mine")
    assert len(res) == 1
    assert res.get("test scope", None) == "Hello World"

    with pytest.warns(UserWarning):
        res = gui.broadcast_callback(print, ["Hello World"], "mine")
        assert isinstance(res, dict)
        assert res.get("test scope", "Hello World") is None

    gui._bindings()._get_or_create_scope("another scope")
    res = gui.broadcast_callback(lambda s, t: t, ["Hello World"], "mine")
    assert len(res) == 2
    assert res.get("test scope", None) == "Hello World"
    assert res.get("another scope", None) == "Hello World"
