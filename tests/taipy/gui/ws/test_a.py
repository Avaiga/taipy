import pytest
from taipy.gui import Gui, Markdown


def test_a_button_pressed(gui: Gui, helpers):
    def do_something_fn(gui, id):
        gui.x = gui.x + 10
        gui.text = "a random text"

    gui.do_something = do_something_fn  # type: ignore
    x = 10  # noqa: F841
    text = "hi"  # noqa: F841
    # Bind test variables
    # assert gui.bind_var_val("x", 10)
    # assert gui.bind_var_val("text", "hi")
    # Bind a page so that the variable will be evaluated as expression
    gui.add_page(
        "test", Markdown("<|Do something!|button|on_action=do_something|id=my_button|> | <|{x}|> | <|{text}|>")
    )
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    flask_client.get(f"/taipy-jsx/test/?client_id={sid}")
    assert gui._scopes.get_all_scopes()[sid].x == 10  # type: ignore
    assert gui._scopes.get_all_scopes()[sid].text == "hi"  # type: ignore
    with pytest.warns(UserWarning):
        ws_client.emit("message", {"type": "A", "name": "my_button", "payload": "do_something"})
    assert gui._scopes.get_all_scopes()[sid].text == "a random text"
    assert gui._scopes.get_all_scopes()[sid].x == 20  # type: ignore
    # assert for received message (message that would be sent to the frontend client)
    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_message(received_messages[0], "MU", "x", 20)
    helpers.assert_outward_ws_message(received_messages[1], "MU", "text", "a random text")
