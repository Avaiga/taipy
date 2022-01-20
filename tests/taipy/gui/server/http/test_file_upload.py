import pytest
from taipy.gui import Gui
import io
import pathlib

def test_file_upload_no_varname(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}")
    assert ret.status_code == 400

def test_file_upload_no_blob(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname"})
    assert ret.status_code == 400

def test_file_upload_no_filename(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    file = (io.BytesIO(b"abcdef"), '')
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname", "blob": "file"})
    assert ret.status_code == 400

def test_file_upload_simple(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file = (io.BytesIO(b"abcdef"), 'test.jpg')
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname", "blob": file}, content_type='multipart/form-data')
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_app_config("upload_folder", ".")) / "test.jpg"
    assert created_file.exists()

def test_file_upload_multi_part(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file0 = (io.BytesIO(b"abcdef"), 'test.jpg')
    file1 = (io.BytesIO(b"abcdef"), 'test.jpg')
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname", "blob": file0, "total" : "2", "part": "0"}, content_type='multipart/form-data')
    assert ret.status_code == 200
    file0_path = pathlib.Path(gui._get_app_config("upload_folder", ".")) / "test.jpg.part.0"
    assert file0_path.exists()
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname", "blob": file1, "total" : "2", "part": "1"}, content_type='multipart/form-data')
    assert ret.status_code == 200
    file1_path = pathlib.Path(gui._get_app_config("upload_folder", ".")) / "test.jpg.part.1"
    assert file1_path.exists()
    file_path = pathlib.Path(gui._get_app_config("upload_folder", ".")) / "test.jpg"
    assert file_path.exists()

def test_file_upload_multiple(gui: Gui, helpers):
    var_name = "varname"
    gui.bind_var_val(var_name, None)
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file = (io.BytesIO(b"abcdef"), 'test.jpg')
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": var_name, "blob": file}, content_type='multipart/form-data')
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_app_config("upload_folder", ".")) / "test.jpg"
    assert created_file.exists()
    file2 = (io.BytesIO(b"abcdef"), 'test2.jpg')
    ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": var_name, "blob": file2, "multiple": "True"}, content_type='multipart/form-data')
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_app_config("upload_folder", ".")) / "test2.jpg"
    assert created_file.exists()
    value =  getattr(gui, var_name)
    assert len(value) == 2

