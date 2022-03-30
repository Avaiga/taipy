import inspect
import pytest

from taipy.gui import Gui, Markdown


def test_default_on_change(gui: Gui, helpers):
    st = {"d": False}

    def on_change(state, var, value):
        st["d"] = True

    x = 10  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page(
        "test", Markdown("<|{x}|input|>")
    )
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test/?client_id={sid}")
    # fake var update
    ws_client.emit("message", {"client_id": sid, "type": "U", "name": "x", "payload": {"value": "20"}})
    assert ws_client.get_received()
    assert st["d"] == True

def test_specific_on_change(gui: Gui, helpers):
    st = {"d": False, "s": False}

    def on_change(state, var, value):
        st["d"] = True

    def on_input_change(state, var, value):
        st["s"] = True

    x = 10  # noqa: F841

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page(
        "test", Markdown("<|{x}|input|on_change=on_input_change|>")
    )
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test/?client_id={sid}")
    # fake var update
    ws_client.emit("message", {"client_id": sid, "type": "U", "name": "x", "payload": {"value": "20", "on_change": "on_input_change"}})
    assert ws_client.get_received()
    assert st["s"] == True
    assert st["d"] == False
