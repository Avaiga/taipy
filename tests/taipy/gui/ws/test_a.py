from taipy.gui import Gui, Markdown


def test_a_button_pressed(gui: Gui, helpers):
    def do_something_fn(gui, id):
        gui.x = gui.x + 10
        gui.text = "a random text"

    gui.do_something = do_something_fn
    # Bind test variables
    assert gui.bind_var_val("x", 10)
    assert gui.bind_var_val("text", "hi")
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test", Markdown("<|Do something!|button|on_action=do_something|id=my_button|> | <|{x}|> | <|{text}|>")
    )
    gui.run(run_server=False)
    assert gui.x == 10
    assert gui.text == "hi"
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get("/flask-jsx/test/")
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server)
    ws_client.emit("message", {"type": "A", "name": "my_button", "payload": "do_something"})
    assert gui._values.text == "a random text"
    assert gui.x == 20
    # assert for received message (message that would be sent to the frontend client)
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_message(received_messages[0], "MU", "x", 20)
    helpers.assert_outward_ws_message(received_messages[1], "MU", "text", "a random text")
