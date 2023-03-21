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
from copy import copy
from datetime import datetime

import pytest

from src.taipy.core._version._version import _Version
from src.taipy.core._version._version_fs_repository_v2 import _VersionFSRepository
from src.taipy.core.cycle._cycle_fs_repository_v2 import _CycleFSRepository
from src.taipy.core.cycle.cycle import Cycle
from src.taipy.core.data import DataNode, InMemoryDataNode
from src.taipy.core.data._data_fs_repository_v2 import _DataFSRepository
from src.taipy.core.exceptions import ModelNotFound
from src.taipy.core.job._job_fs_repository_v2 import _JobFSRepository
from src.taipy.core.job.job import Job
from src.taipy.core.pipeline._pipeline_fs_repository_v2 import _PipelineFSRepository
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_fs_repository_v2 import _ScenarioFSRepository
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_fs_repository_v2 import _TaskFSRepository
from src.taipy.core.task.task import Task
from taipy.config import Config, Frequency, Scope

cycle = Cycle(
    Frequency.DAILY,
    {},
    creation_date=datetime.fromisoformat("2021-11-11T11:11:01.000001"),
    start_date=datetime.fromisoformat("2021-11-11T11:11:01.000001"),
    end_date=datetime.fromisoformat("2021-11-11T11:11:01.000001"),
    name="cc",
)
scenario = Scenario(
    "sc",
    [],
    {},
    None,
    datetime.now(),
    is_primary=False,
    tags={"foo"},
    version="random_version_number",
    cycle=None,
)
pipeline = Pipeline(
    "pipeline",
    {},
    [],
    None,
    owner_id="owner_id",
    parent_ids=set(["parent_id_1", "parent_id_2"]),
    version="random_version_number",
)

data_node = InMemoryDataNode("data_node_config_id", Scope.PIPELINE, version="random_version_number")
task = Task("task_config_id", {}, print, [data_node], [data_node])
job = Job(None, task, "foo")
version = _Version(id="foo", config=Config._applied_config)


class TestFSRepositories:
    @pytest.mark.parametrize(
        "repo,entity,entity_type",
        [
            (_DataFSRepository, data_node, DataNode),
            (_CycleFSRepository, cycle, Cycle),
            (_ScenarioFSRepository, scenario, Scenario),
            (_PipelineFSRepository, pipeline, Pipeline),
            (_TaskFSRepository, task, Task),
            (_JobFSRepository, job, Job),
            (_VersionFSRepository, version, _Version),
        ],
    )
    def test_save_and_load(self, tmpdir, repo, entity, entity_type):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(entity)

        obj = repository._load(entity.id)
        assert isinstance(obj, entity_type)

    @pytest.mark.parametrize(
        "repo,entity",
        [
            (_DataFSRepository, data_node),
            (_CycleFSRepository, cycle),
            (_ScenarioFSRepository, scenario),
            (_PipelineFSRepository, pipeline),
            (_TaskFSRepository, task),
            (_JobFSRepository, job),
            (_VersionFSRepository, version),
        ],
    )
    def test_load_all(self, tmpdir, repo, entity):
        repository = repo()
        repository.base_path = tmpdir
        obj = copy(entity)
        for i in range(10):
            obj.id = None
            repository._save(obj)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize(
        "repo,entity",
        [
            (_DataFSRepository, data_node),
            (_CycleFSRepository, cycle),
            (_ScenarioFSRepository, scenario),
            (_PipelineFSRepository, pipeline),
            (_TaskFSRepository, task),
            (_JobFSRepository, job),
            (_VersionFSRepository, version),
        ],
    )
    def test_load_all_with_filters(self, tmpdir, repo, entity):
        repository = repo()
        repository.base_path = tmpdir
        obj = copy(entity)
        for i in range(10):
            obj.id = None
            obj.owner_id = f"owner_id-{i}"
            repository._save(obj)
        objs = repository._load_all(filters=[{"owner_id": "owner_id-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize(
        "repo,entity",
        [
            (_DataFSRepository, data_node),
            (_CycleFSRepository, cycle),
            (_ScenarioFSRepository, scenario),
            (_PipelineFSRepository, pipeline),
            (_TaskFSRepository, task),
            (_JobFSRepository, job),
            (_VersionFSRepository, version),
        ],
    )
    def test_delete(self, tmpdir, repo, entity):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(entity)

        repository._delete("my_obj_id")

        with pytest.raises(ModelNotFound):
            repository._load("my_obj_id")

    @pytest.mark.parametrize(
        "repo,entity",
        [
            (_DataFSRepository, data_node),
            (_CycleFSRepository, cycle),
            (_ScenarioFSRepository, scenario),
            (_PipelineFSRepository, pipeline),
            (_TaskFSRepository, task),
            (_JobFSRepository, job),
            (_VersionFSRepository, version),
        ],
    )
    def test_delete_all(self, tmpdir, repo, entity):
        repository = repo()
        repository.base_path = tmpdir
        obj = copy(entity)
        for i in range(10):
            obj.id = None
            repository._save(obj)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize(
        "repo,entity",
        [
            (_DataFSRepository, data_node),
            (_CycleFSRepository, cycle),
            (_ScenarioFSRepository, scenario),
            (_PipelineFSRepository, pipeline),
            (_TaskFSRepository, task),
            (_JobFSRepository, job),
            (_VersionFSRepository, version),
        ],
    )
    def test_delete_many(self, tmpdir, repo, entity):
        repository = repo()
        repository.base_path = tmpdir
        obj = copy(entity)

        for i in range(10):
            obj.id = None
            repository._save(obj)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize(
        "repo,entity,entity_type",
        [
            (_DataFSRepository, data_node, DataNode),
            (_CycleFSRepository, cycle, Cycle),
            (_ScenarioFSRepository, scenario, Scenario),
            (_PipelineFSRepository, pipeline, Pipeline),
            (_TaskFSRepository, task, Task),
            (_JobFSRepository, job, Job),
            (_VersionFSRepository, version, _Version),
        ],
    )
    def test_search(self, tmpdir, repo, entity, entity_type):
        repository = repo()
        repository.base_path = tmpdir
        obj = copy(entity)
        for i in range(10):
            obj.id = None
            repository._save(obj)

        assert len(repository._load_all()) == 10

        obj = repository._search("owner_id", "owner_id")

        assert isinstance(obj, entity_type)

    @pytest.mark.parametrize(
        "repo,entity",
        [
            (_DataFSRepository, data_node),
            (_CycleFSRepository, cycle),
            (_ScenarioFSRepository, scenario),
            (_PipelineFSRepository, pipeline),
            (_TaskFSRepository, task),
            (_JobFSRepository, job),
            (_VersionFSRepository, version),
        ],
    )
    def test_export(self, tmpdir, repo, entity):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(entity)

        repository._export("my_obj_id", tmpdir.strpath)
        assert os.path.exists(os.path.join(repo.dir_path, "my_obj_id.json"))
