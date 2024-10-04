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

import json
import logging
import socket
import time
import typing as t
import warnings

from taipy.gui import Gui, Html, Markdown
from taipy.gui._renderers.builder import _Builder
from taipy.gui._warnings import TaipyGuiWarning
from taipy.gui.utils._variable_directory import _reset_name_map
from taipy.gui.utils.expr_var_name import _reset_expr_var_name


class Helpers:
    @staticmethod
    def test_cleanup():
        _Builder._reset_key()
        _reset_name_map()
        _reset_expr_var_name()

    @staticmethod
    def test_control_md(gui: Gui, md_string: str, expected_values: t.Union[str, t.List]):
        gui.add_page("test", Markdown(md_string, frame=None))
        Helpers._test_control(gui, expected_values)

    @staticmethod
    def test_control_html(gui: Gui, html_string: str, expected_values: t.Union[str, t.List]):
        gui.add_page("test", Html(html_string, frame=None))
        Helpers._test_control(gui, expected_values)

    @staticmethod
    def test_control_builder(gui: Gui, builder_page, expected_values: t.Union[str, t.List]):
        gui.add_page("test", builder_page)
        Helpers._test_control(gui, expected_values)

    @staticmethod
    def _test_control(gui: Gui, expected_values: t.Union[str, t.List]):
        gui.run(run_server=False, single_client=True, stylekit=False)
        client = gui._server.test_client()
        response = client.get("/taipy-jsx/test")
        assert response.status_code == 200, f"response.status_code {response.status_code} != 200"
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert isinstance(response_data, t.Dict), "response_data is not Dict"
        assert "jsx" in response_data, "jsx not in response_data"
        jsx = response_data["jsx"]
        logging.getLogger().debug(jsx)
        if isinstance(expected_values, str):
            assert jsx == expected_values, f"{jsx} != {expected_values}"
        elif isinstance(expected_values, list):
            for expected_value in expected_values:
                assert expected_value in jsx, f"{expected_value} not in {jsx}"

    @staticmethod
    def assert_outward_ws_message(received_message, type, varname, value):
        assert isinstance(received_message, dict)
        assert "name" in received_message and received_message["name"] == "message"
        assert "args" in received_message
        args = received_message["args"]
        assert "type" in args and args["type"] == type
        assert "payload" in args
        payload_arr = args["payload"]
        found_payload = False
        for payload in payload_arr:
            if "name" in payload and varname in payload["name"]:
                assert "payload" in payload and "value" in payload["payload"] and payload["payload"]["value"] == value
                found_payload = True
                logging.getLogger().debug(payload["payload"]["value"])
        assert found_payload

    @staticmethod
    def assert_outward_simple_ws_message(received_message, type, varname, value):
        assert isinstance(received_message, dict)
        assert "name" in received_message and received_message["name"] == "message"
        assert "args" in received_message
        args = received_message["args"]
        assert "type" in args and args["type"] == type
        assert "name" in args and args["name"] == varname
        assert "payload" in args
        payload = args["payload"]
        assert "value" in payload and payload["value"] == value
        logging.getLogger().debug(payload["value"])

    @staticmethod
    def assert_outward_ws_simple_message(received_message, aType, values):
        assert isinstance(received_message, dict)
        assert "name" in received_message and received_message["name"] == "message"
        assert "args" in received_message
        args = received_message["args"]
        assert "type" in args and args["type"] == aType
        for k, v in values.items():
            assert k in args and args[k] == v
            logging.getLogger().debug(f"{k}: {args[k]}")

    @staticmethod
    def assert_outward_ws_multiple_message(received_message, type, array_len: int):
        assert isinstance(received_message, dict)
        assert "name" in received_message and received_message["name"] == "message"
        assert "args" in received_message
        args = received_message["args"]
        assert "type" in args and args["type"] == type
        assert "payload" in args
        payload = args["payload"]
        assert isinstance(payload, list)
        assert len(payload) == array_len
        logging.getLogger().debug(payload)

    @staticmethod
    def create_scope_and_get_sid(gui: Gui) -> str:
        sid = "test"
        gui._bindings()._get_or_create_scope(sid)
        return sid

    @staticmethod
    def port_check():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex(("127.0.0.1", 5000)) == 0:
            s.close()
            return True
        else:
            s.close()
            return False

    @staticmethod
    def run_e2e(gui, **kwargs):
        kwargs["run_in_thread"] = True
        kwargs["single_client"] = True
        kwargs["run_browser"] = False
        kwargs["stylekit"] = kwargs.get("stylekit", False)
        with warnings.catch_warnings(record=True):
            gui.run(**kwargs)
        while not Helpers.port_check():
            time.sleep(0.1)

    @staticmethod
    def run_e2e_multi_client(gui: Gui):
        with warnings.catch_warnings(record=True):
            gui.run(run_server=False, run_browser=False, single_client=False, stylekit=False)
            gui._server.run(
                host=gui._get_config("host", "127.0.0.1"),
                port=gui._get_config("port", 5000),
                client_url=gui._get_config("client_url", "http://localhost:{port}"),
                debug=False,
                use_reloader=False,
                flask_log=False,
                run_in_thread=True,
                allow_unsafe_werkzeug=False,
                notebook_proxy=False,
                port_auto_ranges=gui._get_config("port_auto_ranges", None),
            )
        while not Helpers.port_check():
            time.sleep(0.1)

    @staticmethod
    def get_taipy_warnings(warns: t.List[warnings.WarningMessage]) -> t.List[warnings.WarningMessage]:
        return [w for w in warns if w.category is TaipyGuiWarning]
