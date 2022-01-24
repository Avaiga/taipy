from taipy.gui import Gui, Markdown


def test_sending_messages_in_group(gui: Gui, helpers):
    name = "World!" # noqa: F841
    btn_id = "button1" # noqa: F841
    gui.add_page("test", Markdown("<|Hello {name}|button|id={btn_id}|>"))
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # WS client and emit
    ws_client = gui._server._ws.test_client(gui._server.get_flask())
    sid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test/?client_id={sid}")
    assert gui._scopes.get_all_scopes()[sid].name == "World!"  # type: ignore
    assert gui._scopes.get_all_scopes()[sid].btn_id == "button1"  # type: ignore

    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={sid}", data={"client_id": "global"}):
        with gui as aGui:
            setattr(aGui, "name", "Monde!")
            setattr(aGui, "btn_id", "button2")

    assert gui._scopes.get_all_scopes()[sid].name == "Monde!"
    assert gui._scopes.get_all_scopes()[sid].btn_id == "button2"  # type: ignore

    received_messages = ws_client.get_received()
    helpers.assert_outward_ws_multiple_message(received_messages[0], "MS", 2)
