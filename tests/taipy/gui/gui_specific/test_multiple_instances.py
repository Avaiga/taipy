import json

from taipy.gui.gui import Gui


def test_multiple_instance():
    gui1 = Gui("<|gui1|>")
    gui2 = Gui("<|gui2|>")
    gui1.run(run_server=False)
    gui2.run(run_server=False)
    client1 = gui1._server.test_client()
    client2 = gui2._server.test_client()
    assert_multiple_instance(client1, 'value="gui1"')
    assert_multiple_instance(client2, 'value="gui2"')


def assert_multiple_instance(client, expected_value):
    response = client.get("/taipy-jsx/TaiPy_root_page/")
    response_data = json.loads(response.get_data().decode("utf-8", "ignore"))
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "jsx" in response_data
    assert expected_value in response_data["jsx"]
