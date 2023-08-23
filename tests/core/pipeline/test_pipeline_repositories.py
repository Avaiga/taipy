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
from src.taipy.core.pipeline._pipeline_fs_repository import _PipelineFSRepository
from src.taipy.core.pipeline._pipeline_sql_repository import _PipelineSQLRepository
from src.taipy.core.pipeline.pipeline import Pipeline, PipelineId


class TestPipelineRepository:
    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_save_and_load(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(pipeline)

        obj = repository._load(pipeline.id)
        assert isinstance(obj, Pipeline)

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_exists(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(pipeline)

        assert repository._exists(pipeline.id)
        assert not repository._exists("not-existed-pipeline")

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_load_all(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()
        for i in range(10):
            pipeline.id = PipelineId(f"pipeline-{i}")
            repository._save(pipeline)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_load_all_with_filters(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            pipeline.id = PipelineId(f"pipeline-{i}")
            pipeline.owner_id = f"owner-{i}"
            repository._save(pipeline)
        objs = repository._load_all(filters=[{"owner_id": "owner-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_delete(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(pipeline)

        repository._delete(pipeline.id)

        with pytest.raises(ModelNotFound):
            repository._load(pipeline.id)

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_delete_all(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()

        for i in range(10):
            pipeline.id = PipelineId(f"pipeline-{i}")
            repository._save(pipeline)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_delete_many(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()

        for i in range(10):
            pipeline.id = PipelineId(f"pipeline-{i}")
            repository._save(pipeline)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_search(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()

        for i in range(10):
            pipeline.id = PipelineId(f"pipeline-{i}")
            pipeline.owner_id = f"owner-{i}"
            repository._save(pipeline)

        assert len(repository._load_all()) == 10

        objs = repository._search("owner_id", "owner-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Pipeline)

        objs = repository._search("owner_id", "owner-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Pipeline)

        assert repository._search("owner_id", "owner-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("repo", [_PipelineFSRepository, _PipelineSQLRepository])
    def test_export(self, tmpdir, pipeline, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(pipeline)

        repository._export(pipeline.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _PipelineFSRepository else os.path.join(tmpdir.strpath, "pipeline")

        assert os.path.exists(os.path.join(dir_path, f"{pipeline.id}.json"))
