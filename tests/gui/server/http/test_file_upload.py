# Copyright 2021-2025 Avaiga Private Limited
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
import os
import pathlib
import tempfile

import pytest

from taipy.gui import Gui
from taipy.gui.data.data_scope import _DataScopes
from taipy.gui.utils import _get_non_existent_file_path


def test_file_upload_no_varname(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    with pytest.warns(UserWarning):
        ret = server_test_client.post(f"/taipy-uploads?client_id={sid}")
        assert ret.status_code == 400


def test_file_upload_no_blob(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    with pytest.warns(UserWarning):
        ret = server_test_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname"})
        assert ret.status_code == 400


def test_file_upload_no_filename(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    file = (io.BytesIO(b"abcdef"), "")
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    with pytest.warns(UserWarning):
        ret = server_test_client.post(f"/taipy-uploads?client_id={sid}", data={"var_name": "varname", "blob": file})
        assert ret.status_code == 400


@pytest.mark.skip_if_not_server("flask")
def test_file_upload_simple(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file_name = "test.jpg"
    file = (io.BytesIO(b"abcdef"), file_name)
    upload_path = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir()))
    file_name = _get_non_existent_file_path(upload_path, file_name).name
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": "varname", "blob": file},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    created_file = upload_path / file_name
    assert created_file.exists()


@pytest.mark.skip_if_not_server("fastapi")
def test_file_upload_simple_fastapi(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    sid = helpers.create_scope_and_get_sid(gui)
    file_name = "test.jpg"
    file = (io.BytesIO(b"abcdef"), file_name, "image/jpeg")
    upload_path = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir()))
    file_name = _get_non_existent_file_path(upload_path, file_name).name
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        files={"blob": (file[1], file[0], file[2])},
        data={"var_name": "varname"},
    )
    assert ret.status_code == 200
    created_file = upload_path / file_name
    assert created_file.exists()


@pytest.mark.skip_if_not_server("flask")
def test_file_upload_multi_part(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    file_name = "test2.jpg"
    file0 = (io.BytesIO(b"abcdef"), file_name)
    file1 = (io.BytesIO(b"abcdef"), file_name)
    upload_path = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir()))
    file_name = _get_non_existent_file_path(upload_path, file_name).name
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": "varname", "blob": file0, "total": "2", "part": "0"},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": "varname", "blob": file1, "total": "2", "part": "1"},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    file_path = upload_path / file_name
    assert file_path.exists()


@pytest.mark.skip_if_not_server("fastapi")
def test_file_upload_multi_part_fastapi(gui: Gui, helpers):
    gui.run(run_server=False)
    server_test_client = gui._server.test_client()
    sid = helpers.create_scope_and_get_sid(gui)
    file_name = "test2.jpg"
    file0 = (io.BytesIO(b"abcdef"), file_name, "image/jpeg")
    file1 = (io.BytesIO(b"abcdef"), file_name, "image/jpeg")
    upload_path = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir()))
    file_name = _get_non_existent_file_path(upload_path, file_name).name
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        files={"blob": (file0[1], file0[0], file0[2])},
        data={"var_name": "varname", "total": "2", "part": "0"},
    )
    assert ret.status_code == 200
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        files={"blob": (file1[1], file1[0], file1[2])},
        data={"var_name": "varname", "total": "2", "part": "1"},
    )
    assert ret.status_code == 200
    file_path = upload_path / file_name
    assert file_path.exists()


@pytest.mark.skip_if_not_server("flask")
def test_file_upload_multiple(gui: Gui, helpers):
    var_name = "varname"
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    server_test_client = gui._server.test_client()
    with gui.get_app_context():
        gui._bind_var_val(var_name, None)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = _DataScopes._GLOBAL_ID
    file = (io.BytesIO(b"abcdef"), "test.jpg")
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}", data={"var_name": var_name, "blob": file}, content_type="multipart/form-data"
    )
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir())) / "test.jpg"
    assert created_file.exists()
    file2 = (io.BytesIO(b"abcdef"), "test2.jpg")
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        data={"var_name": var_name, "blob": file2, "multiple": "True"},
        content_type="multipart/form-data",
    )
    assert ret.status_code == 200
    created_file = pathlib.Path(gui._get_config("upload_folder", tempfile.gettempdir())) / "test2.jpg"
    assert created_file.exists()
    value = getattr(gui._bindings()._get_all_scopes()[sid], var_name)
    assert len(value) == 2


@pytest.mark.skip_if_not_server("fastapi")
def test_file_upload_multiple_fastapi(gui: Gui, helpers):
    var_name = "varname"
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    server_test_client = gui._server.test_client()
    with gui.get_app_context():
        gui._bind_var_val(var_name, None)
    sid = _DataScopes._GLOBAL_ID
    file1 = (io.BytesIO(b"abcdef"), "test.jpg", "image/jpeg")
    file2 = (io.BytesIO(b"abcdef"), "test2.jpg", "image/jpeg")
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        files={"blob": (file1[1], file1[0], file1[2])},
        data={"var_name": var_name},
    )
    assert ret.status_code == 200
    ret = server_test_client.post(
        f"/taipy-uploads?client_id={sid}",
        files={"blob": (file2[1], file2[0], file2[2])},
        data={"var_name": var_name, "multiple": "True"},
    )
    assert ret.status_code == 200
    value = getattr(gui._bindings()._get_all_scopes()[sid], var_name)
    assert len(value) == 2


@pytest.mark.skip_if_not_server("flask")
def test_file_upload_folder(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    server_test_client = gui._server.test_client()

    sid = _DataScopes._GLOBAL_ID
    files = [(io.BytesIO(b"(^~^)"), "cutey.txt"), (io.BytesIO(b"(^~^)"), "cute_nested.txt")]
    folders = [["folder"], ["folder", "nested"]]
    for file, folder in zip(files, folders):
        path = os.path.join(*folder, file[1])
        response = server_test_client.post(
            f"/taipy-uploads?client_id={sid}",
            data={"var_name": "cute_varname", "blob": file, "path": path},
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        assert os.path.isfile(os.path.join(gui._get_config("upload_folder", tempfile.gettempdir()), path))


@pytest.mark.skip_if_not_server("fastapi")
def test_file_upload_folder_fastapi(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    server_test_client = gui._server.test_client()

    sid = _DataScopes._GLOBAL_ID
    files = [(io.BytesIO(b"(^~^)"), "cutey.txt", "text/plain"), (io.BytesIO(b"(^~^)"), "cute_nested.txt", "text/plain")]
    folders = [["folder"], ["folder", "nested"]]
    for file, folder in zip(files, folders):
        path = os.path.join(*folder, file[1])
        response = server_test_client.post(
            f"/taipy-uploads?client_id={sid}",
            files={"blob": (file[1], file[0], file[2])},
            data={"var_name": "cute_varname", "path": path},
        )
        assert response.status_code == 200
        expected_file_path = os.path.join(gui._get_config("upload_folder", tempfile.gettempdir()), path)
        assert os.path.isfile(expected_file_path)
