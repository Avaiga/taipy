import json
import typing as t

import pytest

from taipy.gui import Gui, Markdown


class Helpers:
    @staticmethod
    def test_control(gui: Gui, md_string: str, expected_values: t.Union[str, t.List]):
        gui.add_page("test", Markdown(md_string))
        gui.run(run_server=False)
        client = gui._server.test_client()
        response = client.get("/flask-jsx/test/")
        print(response.get_data())
        response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
        assert response.status_code == 200
        assert isinstance(response_data, object)
        assert "jsx" in response_data
        jsx = response_data["jsx"]
        if isinstance(expected_values, str):
            assert jsx == expected_values
        elif isinstance(expected_values, list):
            for expected_value in expected_values:
                assert expected_value in jsx


@pytest.fixture
def helpers():
    return Helpers
