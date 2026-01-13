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


from taipy.gui import Gui, Markdown


def test_variable_binding(helpers, gui_server):
    x = "a string"  # noqa: F841
    gui = Gui(server=gui_server)
    gui.add_page("test", Markdown("<|{not x}|>"))
    gui.run(run_server=False, single_client=True)
    client = gui._server.test_client()
    client.get(f"/{Gui._JSX_URL}/test")
    fv_set = gui._Gui__front_end_variables # type: ignore[reportAttributeAccessIssue]
    assert len(fv_set) == 1
    assert "x" not in fv_set
    helpers.test_cleanup()
