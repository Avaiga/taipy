from taipy.gui import Gui, Markdown


def test_ru_selector(gui: Gui, helpers, csvdata):
    # Bind test variables
    selected_val = ["value1", "value2"]  # noqa: F841
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test",
        Markdown("<|{selected_val}|selector|multiple|>"),
    )
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    sid = list(gui._data_scopes.get_all_scopes().keys())[1]
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/flask-jsx/test/?client_id={sid}")
    ws_client.emit("message", {"type": "RU", "name": "", "payload": {"names": ["selected_val"]}})
    # assert for received message (message that would be sent to the frontend client)
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_message(received_messages[0], "MU", "selected_val", ["value1", "value2"])
