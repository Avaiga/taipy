import json
import logging
import typing as t

from taipy.gui import Gui, Html, Markdown
from taipy.gui.renderers.builder import Builder


class Helpers:
    @staticmethod
    def test_cleanup():
        Builder._reset_key()
        del Gui._instances[Gui]

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
        response = client.get("/flask-jsx/test/")
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
