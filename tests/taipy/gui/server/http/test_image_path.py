import pytest
from taipy.gui import Gui
import pathlib

def test_image_path_not_found(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.get(f"/taipy-images/images/img.png?client_id={sid}")
    assert ret.status_code == 404

def test_image_path_found(gui: Gui, helpers):
    url = gui._get_image_content("img", str((pathlib.Path(__file__).parent.parent.parent / "resources" / "fred.png").resolve()), False)
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.get(f"{url}?client_id={sid}")
    assert ret.status_code == 200
