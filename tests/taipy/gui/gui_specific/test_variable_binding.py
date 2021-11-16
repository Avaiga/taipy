from types import FunctionType

from taipy.gui import Gui, Markdown


def test_variable_binding_1(helpers):
    """
    Test locals binding of a function and 3 variables
    """

    def another_function(gui):
        print("Hello World!")

    x = 10
    y = 20
    z = "Hello World!"
    gui = Gui(__name__)
    gui.add_page("test", Markdown("<|{x}|> | <|{y}|> | <|{z}|button|on_action=another_function|>"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    client.get("/flask-jsx/test/")
    assert gui.x == x
    assert gui.y == y
    assert gui.z == z
    assert isinstance(gui.another_function, FunctionType)
    helpers.test_cleanup()


def test_variable_binding_2(helpers):
    """
    Test locals binding of a function and 3 variables, now with button properties usage
    """

    def another_function(gui):
        print("Hello World!")

    x = 10
    y = 20
    z = "Hello World!"
    label = "an label"
    button_properties = {"label": label, "on_action": "another_function"}  # noqa: F841
    gui = Gui(__name__)
    gui.add_page("test", Markdown("<|{x}|> | <|{y}|> | <|{z}|button|properties=button_properties|>"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    client.get("/flask-jsx/test/")
    assert gui.x == x
    assert gui.y == y
    assert gui.z == z
    assert isinstance(gui.another_function, FunctionType)
    helpers.test_cleanup()
