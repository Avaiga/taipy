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

from taipy.gui import Gui, Markdown

from .state_asset.page1 import get_a, md_page1, set_a


def test_state(gui: Gui):
    a = 10  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page("page1", md_page1)
    gui.run(run_server=False, single_client=True)
    state = gui._Gui__state
    with gui.get_flask_app().app_context():
        assert state.a == 10
        assert state["page1"].a == 20
        assert state["tests.gui.gui_specific.state_asset.page1"].a == 20
        assert state._gui == gui
        with pytest.raises(Exception) as e:
            state.b
        assert e.value.args[0] == "Variable 'b' is not defined."

        with pytest.raises(Exception) as e:
            state.b = 10
        assert e.value.args[0] == "Variable 'b' is not accessible."

        with pytest.raises(Exception) as e:
            state._taipy_p1
        assert e.value.args[0] == "Variable '_taipy_p1' is protected and is not accessible."

        with pytest.raises(Exception) as e:
            state._taipy_p1 = 10
        assert e.value.args[0] == "Variable '_taipy_p1' is not accessible."

        assert state._get_placeholder("_taipy_p1") is None

        state._set_placeholder("_taipy_p1", 10)

        assert state._get_placeholder("_taipy_p1") == 10

        assert state._get_placeholder_attrs() == (
            "_taipy_p1",
            "_current_context",
        )

        assert get_a(state) == 20

        set_a(state, 30)

        assert get_a(state) == 30
