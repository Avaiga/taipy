import inspect
import json
import logging
import socket
import time
import typing as t
import warnings
from types import FrameType

from taipy.gui import Gui, Html, Markdown
from taipy.gui.renderers.builder import _Builder


class Helpers:
    @staticmethod
    def test_cleanup():
        _Builder._reset_key()

    @staticmethod
    def test_control_md(gui: Gui, md_string: str, expected_values: t.Union[str, t.List]):
        gui.add_page("test", Markdown(md_string))
        Helpers._test_control(gui, expected_values)

    @staticmethod
    def test_control_html(gui: Gui, html_string: str, expected_values: t.Union[str, t.List]):
        gui.add_page("test", Html(html_string))
        Helpers._test_control(gui, expected_values)

    @staticmethod
    def _test_control(gui: Gui, expected_values: t.Union[str, t.List]):
        gui.run(run_server=False)
        client = gui._server.test_client()
        response = client.get("/taipy-jsx/test/")
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert isinstance(response_data, t.Dict)
        assert "jsx" in response_data
        jsx = response_data["jsx"]
        logging.getLogger().debug(jsx)
        if isinstance(expected_values, str):
            assert jsx == expected_values
        elif isinstance(expected_values, list):
            for expected_value in expected_values:
                assert expected_value in jsx

    @staticmethod
    def assert_outward_ws_message(received_message, type, varname, value):
        assert isinstance(received_message, dict)
        assert "name" in received_message and received_message["name"] == "message"
        assert "args" in received_message
        args = received_message["args"]
        assert "type" in args and args["type"] == type
        assert "payload" in args
        payload = args["payload"][0]
        assert "name" in payload and payload["name"] == varname
        assert "payload" in payload and "value" in payload["payload"] and payload["payload"]["value"] == value
        logging.getLogger().debug(payload["payload"]["value"])

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
        kwargs["locals_bind"] = t.cast(FrameType, inspect.currentframe().f_back).f_locals
        with warnings.catch_warnings(record=True):
            gui.run(**kwargs)
        while not Helpers.port_check():
            time.sleep(0.1)
