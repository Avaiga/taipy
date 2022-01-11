import pytest
from types import FunctionType
from taipy.gui import Gui, Markdown


def test_variable_binding(helpers):
    """
    Tests the binding of a few variables and a function
    """

    def another_function(gui):
        pass

    x = 10
    y = 20
    z = "button label"
    gui = Gui(__name__)
    gui.add_page("test", Markdown("<|{x}|> | <|{y}|> | <|{z}|button|on_action=another_function|>"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    jsx = client.get("/flask-jsx/test/").json["jsx"]
    for expected in ["<Button", f'defaultLabel="{z}"', "label={z}"]:
        assert expected in jsx
    assert gui.x == x
    assert gui.y == y
    assert gui.z == z
    assert isinstance(gui.another_function, FunctionType)
    helpers.test_cleanup()


def test_properties_binding(helpers):
    gui = Gui(__name__)
    modifier = "nice "  # noqa: F841
    button_properties = {"label": "A {modifier}button"}  # noqa: F841
    gui.add_page("test", Markdown("<|button|properties=button_properties|>"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    jsx = client.get("/flask-jsx/test/").json["jsx"]
    for expected in ["<Button", 'defaultLabel="A nice button"']:
        assert expected in jsx
    helpers.test_cleanup()


def test_dict_binding(helpers):
    """
    Tests the binding of a dictionary property
    """

    d = {"k": "test"}  # noqa: F841
    gui = Gui(__name__, Markdown("<|{d.k}|>"))
    gui.run(run_server=False)
    client = gui._server.test_client()
    jsx = client.get("/flask-jsx/TaiPy_root_page/").json["jsx"]
    for expected in ["<Field", 'defaultValue="test"']:
        assert expected in jsx
    helpers.test_cleanup()
