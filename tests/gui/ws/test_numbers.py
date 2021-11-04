from taipy.gui import Gui, Markdown


def test_ws_numbers(gui: Gui):
    # Bind a variable
    assert gui.bind_var_val("x", 10)
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page("test", Markdown("<|{x}|>"))
    gui.run(run_server=False)
    assert gui.x == 10
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get("/flask-jsx/test/")
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server)
    ws_client.emit("message", {"type": "U", "name": "x", "payload": "11"})
    assert gui.x == 11
