# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
import os
import pathlib
import shutil

import pytest

from taipy.core.exceptions.exceptions import ModelNotFound

from .mocks import MockConverter, MockFSRepository, MockModel, MockObj


class TestRepositoriesStorage:
    def test_load_from_non_existent_file_on_fs_repo(self):
        r = MockFSRepository(model_type=MockModel, dir_name="mock_model", converter=MockConverter)

        # The file does not exist should raise ModelNotFound exception
        with pytest.raises(ModelNotFound):
            r._load("non_existent_file")

        # The file exists but is empty should also raise ModelNotFound exception
        os.makedirs(r.dir_path)
        with open(r.dir_path / "empty_file.json", "w") as f:
            f.write("")

        assert r._exists("empty_file")
        with pytest.raises(ModelNotFound):
            r._load("empty_file")

    @pytest.mark.parametrize(
        "mock_repo,params",
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    def test_save_and_fetch_model(self, mock_repo, params):
        r = mock_repo(**params)
        m = MockObj("uuid", "foo")
        r._save(m)

        fetched_model = r._load(m.id)
        assert m == fetched_model

    @pytest.mark.parametrize(
        "mock_repo,params",
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    def test_exists(self, mock_repo, params):
        r = mock_repo(**params)
        m = MockObj("uuid", "foo")
        r._save(m)

        assert r._exists(m.id)
        assert not r._exists("not-existed-model")

    @pytest.mark.parametrize(
        "mock_repo,params",
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    def test_get_all(self, mock_repo, params):
        objs = []
        r = mock_repo(**params)
        r._delete_all()

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
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    def test_delete_all(self, mock_repo, params):
        r = mock_repo(**params)
        r._delete_all()

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
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    def test_delete_many(self, mock_repo, params):
        r = mock_repo(**params)
        r._delete_all()

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
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    def test_search(self, mock_repo, params):
        r = mock_repo(**params)
        r._delete_all()

        m = MockObj("uuid", "foo")
        r._save(m)

        m1 = r._search("name", "bar")
        m2 = r._search("name", "foo")

        assert m1 == []
        assert m2 == [m]

    @pytest.mark.parametrize(
        "mock_repo,params",
        [
            (MockFSRepository, {"model_type": MockModel, "dir_name": "mock_model", "converter": MockConverter}),
        ],
    )
    @pytest.mark.parametrize("export_path", ["tmp"])
    def test_export(self, mock_repo, params, export_path):
        r = mock_repo(**params)

        m = MockObj("uuid", "foo")
        r._save(m)

        r._export("uuid", export_path)
        assert pathlib.Path(os.path.join(export_path, "mock_model/uuid.json")).exists()
        with open(os.path.join(export_path, "mock_model/uuid.json"), "r") as exported_file:
            exported_data = json.load(exported_file)
            assert exported_data["id"] == "uuid"
            assert exported_data["name"] == "foo"

        # Export to same location again should work
        r._export("uuid", export_path)
        assert pathlib.Path(os.path.join(export_path, "mock_model/uuid.json")).exists()

        shutil.rmtree(export_path, ignore_errors=True)
