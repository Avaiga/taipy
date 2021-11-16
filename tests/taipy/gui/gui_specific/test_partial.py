import json

from taipy.gui import Gui, Markdown


def test_partial(gui: Gui):
    gui.add_partial(Markdown("#This is a partial"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    response = client.get(f"/flask-jsx/{gui._config.partial_routes[0]}/")
    response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
    assert response.status_code == 200
    assert "jsx" in response_data and "This is a partial" in response_data["jsx"]
