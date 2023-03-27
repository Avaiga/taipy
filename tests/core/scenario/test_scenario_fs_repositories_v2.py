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

import os

import pytest

from src.taipy.core.exceptions import ModelNotFound
from src.taipy.core.scenario._scenario_fs_repository_v2 import _ScenarioFSRepository
from src.taipy.core.scenario.scenario import Scenario, ScenarioId


class TestScenarioFSRepository:
    def test_save_and_load(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir
        repository._save(scenario)

        obj = repository._load(scenario.id)
        assert isinstance(obj, Scenario)

    def test_load_all(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir
        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    def test_load_all_with_filters(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            scenario.name = f"scenario-{i}"
            repository._save(scenario)
        objs = repository._load_all(filters=[{"name": "scenario-2"}])

        assert len(objs) == 1

    def test_delete(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir
        repository._save(scenario)

        repository._delete(scenario.id)

        with pytest.raises(ModelNotFound):
            repository._load(scenario.id)

    def test_delete_all(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    def test_delete_many(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    def test_search(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            scenario.name = f"scenario-{i}"
            repository._save(scenario)

        assert len(repository._load_all()) == 10

        obj = repository._search("name", "scenario-2")

        assert isinstance(obj, Scenario)

    def test_export(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository.base_path = tmpdir
        repository._save(scenario)

        repository._export(scenario.id, tmpdir.strpath)
        assert os.path.exists(os.path.join(repository.dir_path, f"{scenario.id}.json"))
