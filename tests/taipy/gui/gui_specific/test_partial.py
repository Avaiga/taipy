import json
from types import SimpleNamespace

from taipy.gui import Gui, Markdown


def test_partial(gui: Gui):
    gui.add_partial(Markdown("#This is a partial"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    response = client.get(f"/taipy-jsx/{gui._config.partial_routes[0]}/")
    response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
    assert response.status_code == 200
    assert "jsx" in response_data and "This is a partial" in response_data["jsx"]

def test_partial_update(gui: Gui):
    partial = gui.add_partial(Markdown("#This is a partial"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    response = client.get(f"/taipy-jsx/{gui._config.partial_routes[0]}/")
    response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
    assert response.status_code == 200
    assert "jsx" in response_data and "This is a partial" in response_data["jsx"]
    # update partial
    fake_state = SimpleNamespace()
    fake_state._gui = gui
    partial.update_content(fake_state, "#partial updated")
    response = client.get(f"/taipy-jsx/{gui._config.partial_routes[0]}/")
    response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
    assert response.status_code == 200
    assert "jsx" in response_data and "partial updated" in response_data["jsx"]
