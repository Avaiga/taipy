from taipy.gui import Gui, Markdown


def test_du_table_data_fetched(gui: Gui, helpers, csvdata):
    # Bind test variables
    assert gui.bind_var_val("selected_val", ["value1", "value2"])
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test",
        Markdown("<|{selected_val}|selector|multiple|>"),
    )
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get("/flask-jsx/test/")
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server)
    ws_client.emit("message", {"type": "RU", "name": "", "payload": {"names": ["selected_val"]}})
    # assert for received message (message that would be sent to the frontend client)
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_message(received_messages[0], "MU", "selected_val", ["value1", "value2"])
