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
    """
    Tests the binding of a few variables and a function
    """

    def another_function(gui):
        pass

    x = 10
    y = 20
    z = "button label"
    gui = Gui(server=gui_server)
    gui.add_page("test", Markdown("<|{x}|> | <|{y}|> | <|{z}|button|on_action=another_function|>"))
    gui.run(run_server=False, single_client=True)
    client = gui._server.test_client()
    response = client.get(f"/{Gui._JSX_URL}/test")
    jsx = helpers.get_response_data(response, gui)["jsx"]
    for expected in ["<Button", 'defaultLabel="button label"', 'label="{!tpec_TpExPr_z_TPMDL_0']:
        assert expected in jsx
    assert gui._bindings().x == x # type: ignore[reportAttributeAccessIssue]
    assert gui._bindings().y == y # type: ignore[reportAttributeAccessIssue]
    assert gui._bindings().z == z # type: ignore[reportAttributeAccessIssue]
    with gui.get_app_context():
        assert callable(gui._get_user_function("another_function"))
    helpers.test_cleanup()


def test_properties_binding(helpers, gui_server):
    gui = Gui(server=gui_server)
    modifier = "nice "  # noqa: F841
    button_properties = {"label": "A {modifier}button"}  # noqa: F841
    gui.add_page("test", Markdown("<|button|properties=button_properties|>"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    response = client.get(f"/{Gui._JSX_URL}/test")
    jsx = helpers.get_response_data(response, gui)["jsx"]
    for expected in ["<Button", 'defaultLabel="A nice button"']:
        assert expected in jsx
    helpers.test_cleanup()


def test_dict_binding(helpers, gui_server):
    """
    Tests the binding of a dictionary property
    """
    d = {"k": "test"}  # noqa: F841
    gui = Gui("<|{d.k}|>", server=gui_server)
    gui.run(run_server=False)
    client = gui._server.test_client()
    response = client.get(f"/{Gui._JSX_URL}/TaiPy_root_page")
    jsx = helpers.get_response_data(response, gui)["jsx"]
    for expected in ["<Field", 'defaultValue="test"']:
        assert expected in jsx
    helpers.test_cleanup()
