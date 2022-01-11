from taipy.gui import Gui, Html


def test_simple_html(gui: Gui, helpers):
    # html_string = "<html><head></head><body><h1>test</h1><taipy:field value=\"test\"/></body></html>"
    html_string = "<html><head></head><body><h1>test</h1></body></html>"
    gui.add_page("test", Html(html_string))
    gui.run(run_server=False)
    client = gui._server.test_client()
    jsx = client.get("/flask-jsx/test/").json["jsx"]
    assert jsx == "<h1>test</h1>"
