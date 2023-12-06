# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import inspect
import io
import pathlib
import tempfile
from unittest.mock import patch

import pytest

from taipy.gui import Gui
from taipy.gui.data.data_scope import _DataScopes
from taipy.gui.utils import _get_non_existent_file_path


def test_file_upload_no_varname(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    with pytest.warns(UserWarning):
        ret = flask_client.post(f"/taipy-uploads?client_id={sid}")
        assert ret.status_code == 400


def test_file_upload_no_blob(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    with pytest.warns(UserWarning):
        ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname"})
        assert ret.status_code == 400


def test_file_upload_no_filename(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    file = (io.BytesIO(b"abcdef"), "")
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    with pytest.warns(UserWarning):
        ret = flask_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname", "blob": file})
        assert ret.status_code == 400


def test_file_upload_simple(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file_name = "test.jpg"
    file = (io.BytesIO(b"abcdef"), file_name)
    upload_path = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir()))
    file_name = _get_non_existent_file_path(upload_path, file_name).name
    ret = flask_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": "varname", "blob": file},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    created_file = upload_path / file_name
    assert created_file.exists()


def test_file_upload_multi_part(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file_name = "test2.jpg"
    file0 = (io.BytesIO(b"abcdef"), file_name)
    file1 = (io.BytesIO(b"abcdef"), file_name)
    upload_path = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir()))
    file_name = _get_non_existent_file_path(upload_path, file_name).name
    ret = flask_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": "varname", "blob": file0, "total": "2", "part": "0"},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    file0_path = upload_path / f"{file_name}.part.0"
    assert file0_path.exists()
    ret = flask_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": "varname", "blob": file1, "total": "2", "part": "1"},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    file1_path = upload_path / f"{file_name}.part.1"
    assert file1_path.exists()
    file_path = upload_path / file_name
    assert file_path.exists()


def test_file_upload_multiple(gui: Gui, helpers):
    var_name = "varname"
    gui._set_frame(inspect.currentframe())
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    flask_client = gui._server.test_client()
    with gui.get_flask_app().app_context():
        gui._bind_var_val(var_name, None)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = _DataScopes._GLOBAL_ID
    file = (io.BytesIO(b"abcdef"), "test.jpg")
    ret = flask_client.post(
        f"/taipy-uploads?client_id={sid}", data={"var_name": var_name, "blob": file}, content_type="multipart/form-data"
    )
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir())) / "test.jpg"
    assert created_file.exists()
    file2 = (io.BytesIO(b"abcdef"), "test2.jpg")
    ret = flask_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": var_name, "blob": file2, "multiple": "True"},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir())) / "test2.jpg"
    assert created_file.exists()
    value = getattr(gui._bindings()._get_all_scopes()[sid], var_name)
    assert len(value) == 2
