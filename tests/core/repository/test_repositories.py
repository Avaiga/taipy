# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import json
import pathlib
import shutil

import pytest

from src.taipy.core.exceptions.exceptions import InvalidExportPath
from taipy.config.config import Config

from .mocks import MockFSRepository, MockSQLRepository, MockModel, MockObj


class TestRepositoriesStorage:
    @pytest.mark.parametrize(
        "mock_repo,params",
        [(MockFSRepository, {"model": MockModel, "dir_name": "foo"})],
    )
    def test_save_and_fetch_model(self, mock_repo, params):

        r = mock_repo(**params)
        m = MockObj("uuid", "foo")
        r._save(m)

        fetched_model = r.load(m.id)
        assert m == fetched_model

    @pytest.mark.parametrize(
        "mock_repo,params",
        [(MockFSRepository, {"model": MockModel, "dir_name": "foo"})],
    )
    def test_get_all(self, mock_repo, params):

        objs = []
        r = mock_repo(**params)
        for i in range(5):
            m = MockObj(f"uuid-{i}", f"Foo{i}")
            objs.append(m)
            r._save(m)
        _objs = r._load_all()

        assert len(_objs) == 5

        for obj in _objs:
            assert isinstance(obj, MockObj)
        assert sorted(objs, key=lambda o: o.id) == sorted(_objs, key=lambda o: o.id)

    @pytest.mark.parametrize(
        "mock_repo,params",
        [(MockFSRepository, {"model": MockModel, "dir_name": "foo"})],
    )
    def test_delete_all(self, mock_repo, params):
        r = mock_repo(**params)

        for i in range(5):
            m = MockObj(f"uuid-{i}", f"Foo{i}")
            r._save(m)

        _models = r._load_all()
        assert len(_models) == 5

        r._delete_all()
        _models = r._load_all()
        assert len(_models) == 0

    @pytest.mark.parametrize(
        "mock_repo,params",
        [(MockFSRepository, {"model": MockModel, "dir_name": "foo"})],
    )
    def test_delete_many(self, mock_repo, params):

        r = mock_repo(**params)
        for i in range(5):
            m = MockObj(f"uuid-{i}", f"Foo{i}")
            r._save(m)

        _models = r._load_all()
        assert len(_models) == 5
        r._delete_many(["uuid-0", "uuid-1"])
        _models = r._load_all()
        assert len(_models) == 3

    @pytest.mark.parametrize(
        "mock_repo,params",
        [(MockFSRepository, {"model": MockModel, "dir_name": "foo"})],
    )
    def test_search(self, mock_repo, params):
        r = mock_repo(**params)

        m = MockObj("uuid", "foo")
        r._save(m)

        m1 = r._search("name", "bar")
        m2 = r._search("name", "foo")

        assert m1 is None
        assert m == m2

    @pytest.mark.parametrize(
        "mock_repo,params",
        [
            (MockFSRepository, {"model": MockModel, "dir_name": "mock_model"}),
            (MockSQLRepository, {"model": MockModel}),
        ],
    )
    @pytest.mark.parametrize("export_path", ["tmp"])
    def test_export(self, mock_repo, params, tmp_sqlite, export_path):
        if mock_repo == MockSQLRepository:
            Config.global_config.repository_properties = {"db_location": tmp_sqlite}

        r = mock_repo(**params)

        m = MockObj("uuid", "foo")
        r._save(m)

        r._export("uuid", export_path)
        assert pathlib.Path(os.path.join(export_path, f"mock_model/uuid.json")).exists()
        with open(os.path.join(export_path, f"mock_model/uuid.json"), "r") as exported_file:
            exported_data = json.load(exported_file)
            assert exported_data["id"] == "uuid"
            assert exported_data["name"] == "foo"

        # Export to same location again should work
        r._export("uuid", export_path)
        assert pathlib.Path(os.path.join(export_path, f"mock_model/uuid.json")).exists()

        if mock_repo == MockFSRepository:
            with pytest.raises(InvalidExportPath):
                r._export("uuid", Config.global_config.storage_folder)

        shutil.rmtree(export_path, ignore_errors=True)

    def test_config_override(self):
        storage_folder = pathlib.Path("/tmp") / "fodo"
        repo = MockFSRepository(model=MockModel, dir_name="mock")

        assert repo.dir_path == pathlib.Path(".data") / "mock"
        Config.configure_global_app(storage_folder=str(storage_folder))
        assert repo.dir_path == storage_folder / "mock"
