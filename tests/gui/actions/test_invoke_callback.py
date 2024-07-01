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

from flask import g

from taipy.gui import Gui, Markdown, State


@contextlib.contextmanager
def get_state(gui: Gui, state_id: str):
    with gui.get_flask_app().app_context():
        client_id = gui._bindings()._get_or_create_scope(state_id)[0]
        gui._Gui__set_client_id_in_context(client_id)  # type: ignore[attr-defined]
        yield gui._Gui__state  # type: ignore[attr-defined]


def test_invoke_callback(gui: Gui, helpers):
    name = "World!"  # noqa: F841
    btn_id = "button1"  # noqa: F841

    val = 1  # noqa: F841

    def user_callback(state: State):
        state.val = 10

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello {name}|button|id={btn_id}|>\n<|{val}|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # client id
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")

    gui.invoke_callback(cid, user_callback, [])
    with get_state(gui, cid) as state:
        assert state.val == 10


def test_invoke_callback_sid(gui: Gui, helpers):
    name = "World!"  # noqa: F841
    btn_id = "button1"  # noqa: F841

    val = 1  # noqa: F841

    def user_callback(state: State):
        state.val = 10

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello {name}|button|id={btn_id}|>\n<|{val}|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # client id
    cid = helpers.create_scope_and_get_sid(gui)
    base_sid, _ = gui._bindings()._get_or_create_scope("base sid")

    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().app_context():
        g.client_id = base_sid
        gui.invoke_callback(cid, user_callback, [])
        assert g.client_id == base_sid

    with get_state(gui, base_sid) as base_state:
        assert base_state.val == 1
    with get_state(gui, cid) as a_state:
        assert a_state.val == 10
