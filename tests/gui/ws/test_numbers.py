from taipy.gui import Gui, Markdown

def test_ws_numbers(gui: Gui):
    # Bind a variable
    assert gui.bind_var_val("var", 10)
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page("test", Markdown("<|{var}|>"))
    gui.run(run_server=False)
    assert gui.var == 10
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get("/flask-jsx/test/")
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server)
    ws_client.emit("message", {"type": "U", "name": "var", "payload": "11"})
    assert gui.var == 11
    # assert for received message (message that would be sent to the frontend client)
    received_message = ws_client.get_received()[0]
    assert isinstance(received_message, dict)
    assert "name" in received_message and received_message["name"] == "message"
    assert "args" in received_message
    args = received_message["args"]
    assert "type" in args and args["type"] == "MU"
    assert "payload" in args
    payload = args["payload"][0]
    assert "name" in payload and payload["name"] == "var"
    assert "payload" in payload and payload["payload"]["value"] == 11
