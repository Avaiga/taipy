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

import os

import pytest

from taipy.core.exceptions import ModelNotFound
from taipy.core.scenario._scenario_fs_repository import _ScenarioFSRepository
from taipy.core.scenario.scenario import Scenario, ScenarioId


class TestScenarioFSRepository:
    def test_save_and_load(self, scenario: Scenario):
        repository = _ScenarioFSRepository()
        repository._save(scenario)

        loaded_scenario = repository._load(scenario.id)
        assert isinstance(loaded_scenario, Scenario)
        assert scenario._config_id == loaded_scenario._config_id
        assert scenario.id == loaded_scenario.id
        assert scenario._tasks == loaded_scenario._tasks
        assert scenario._additional_data_nodes == loaded_scenario._additional_data_nodes
        assert scenario._creation_date == loaded_scenario._creation_date
        assert scenario._cycle == loaded_scenario._cycle
        assert scenario._primary_scenario == loaded_scenario._primary_scenario
        assert scenario._tags == loaded_scenario._tags
        assert scenario._properties == loaded_scenario._properties
        assert scenario._sequences == loaded_scenario._sequences
        assert scenario._version == loaded_scenario._version

    def test_exists(self, scenario):
        repository = _ScenarioFSRepository()
        repository._save(scenario)

        assert repository._exists(scenario.id)
        assert not repository._exists("not-existed-scenario")

    def test_load_all(self, scenario):
        repository = _ScenarioFSRepository()
        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    def test_load_all_with_filters(self, scenario):
        repository = _ScenarioFSRepository()

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)
        objs = repository._load_all(filters=[{"id": "scenario-2"}])

        assert len(objs) == 1

    def test_delete(self, scenario):
        repository = _ScenarioFSRepository()
        repository._save(scenario)

        repository._delete(scenario.id)

        with pytest.raises(ModelNotFound):
            repository._load(scenario.id)

    def test_delete_all(self, scenario):
        repository = _ScenarioFSRepository()

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    def test_delete_many(self, scenario):
        repository = _ScenarioFSRepository()

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    def test_delete_by(self, scenario):
        repository = _ScenarioFSRepository()

        # Create 5 entities with version 1.0 and 5 entities with version 2.0
        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            scenario._version = f"{(i+1) // 5}.0"
            repository._save(scenario)

        objs = repository._load_all()
        assert len(objs) == 10
        repository._delete_by("version", "1.0")

        assert len(repository._load_all()) == 5

    def test_search(self, scenario):
        repository = _ScenarioFSRepository()

        for i in range(10):
            scenario.id = ScenarioId(f"scenario-{i}")
            repository._save(scenario)

        assert len(repository._load_all()) == 10

        objs = repository._search("id", "scenario-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Scenario)

        objs = repository._search("id", "scenario-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Scenario)

        assert repository._search("id", "scenario-2", filters=[{"version": "non_existed_version"}]) == []

    def test_export(self, tmpdir, scenario):
        repository = _ScenarioFSRepository()
        repository._save(scenario)

        repository._export(scenario.id, tmpdir.strpath)
        dir_path = repository.dir_path

        assert os.path.exists(os.path.join(dir_path, f"{scenario.id}.json"))
