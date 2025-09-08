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

import inspect
import warnings

import pytest

from taipy.gui import Gui, Markdown


class _AType:
    pass


def test_register_content_provider(gui: Gui, helpers):
    def content_provider(x):
        return x

    gui.register_content_provider(_AType, content_provider)
    assert gui._Gui__content_providers[_AType] is content_provider  # type: ignore[attr-defined]


def test_bad_register_content_provider(gui: Gui, helpers):
    with warnings.catch_warnings(record=True) as records:
        gui.register_content_provider(_AType, "content_provider")  # type: ignore[arg-type]
        assert len(records) == 1


def test_bad_again_register_content_provider(gui: Gui, helpers):
    def content_provider(x):
        return x

    with warnings.catch_warnings(record=True) as records:
        gui.register_content_provider(_AType, content_provider)
        gui.register_content_provider(_AType, content_provider)
        assert len(records) == 1


@pytest.mark.skip(reason="Server Error on CI, but works locally")
def test_process_content_provider(gui: Gui, helpers):
    def content_provider(x):
        return f"instance of {type(x)}"

    an_instance = _AType()  # noqa: F841

    gui.register_content_provider(_AType, content_provider)

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello {str(an_instance)}|button|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    # my content provider
    result = server_test_client.get(
        f"/taipy-user-content/test?client_id={cid}&__taipy_html_content=true&variable_name=an_instance"
    )
    assert "instance of <class 'test_content_provider._AType'>" in result.data.decode()


def test_process_content_provider_invalid(gui: Gui, helpers):
    v_name = "variable"  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello {v_name}|button|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    # no content provider
    result = server_test_client.get(
        f"/taipy-user-content/test?client_id={cid}&__taipy_html_content=true&variable_name=v_name"
    )
    assert "No valid provider" in helpers.get_response_raw_data(result, gui)


def test__serve_user_content(gui: Gui, helpers):
    def user_content(x):
        return f"instance of {type(x)}"

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello |button|on_action=user_content|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    # no content provider
    result = server_test_client.get(f"/taipy-user-content/test?client_id={cid}&custom_user_content_cb=user_content")
    assert "taipy.gui.state._GuiState" in helpers.get_response_raw_data(result, gui)


def test__serve_user_content_bad(gui: Gui, helpers):
    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", Markdown("<|Hello |button|>"))
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    server_test_client.get(f"/{Gui._JSX_URL}/test?client_id={cid}")
    # no content provider
    with warnings.catch_warnings(record=True) as records:
        server_test_client.get(f"/taipy-user-content/test?client_id={cid}&custom_user_content_cb=bad_user_content")
        assert len(records) == 2
