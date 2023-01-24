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

from src.taipy.core.pipeline._pipeline_repository_factory import _PipelineRepositoryFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from taipy.config.config import Config


class TestPipelineRepository:
    def test_save_and_load(self, tmpdir, pipeline):
        repository = _PipelineRepositoryFactory._build_repository()
        repository.base_path = tmpdir
        repository._save(pipeline)
        loaded_pipeline = repository.load("pipeline_id")

        assert isinstance(loaded_pipeline, Pipeline)
        assert pipeline.id == loaded_pipeline.id

    def test_from_and_to_model(self, pipeline, pipeline_model):
        repository = _PipelineRepositoryFactory._build_repository()
        assert repository._to_model(pipeline) == pipeline_model
        assert repository._from_model(pipeline_model) == pipeline

    def test_save_and_load_with_sql_repo(self, tmpdir, pipeline):
        Config.configure_global_app(repository_type="sql")
        repository = _PipelineRepositoryFactory._build_repository()

        repository.base_path = tmpdir
        repository._save(pipeline)
        loaded_pipeline = repository.load("pipeline_id")

        assert isinstance(loaded_pipeline, Pipeline)
        assert pipeline.id == loaded_pipeline.id

    def test_from_and_to_model_with_sql_repo(self, pipeline, pipeline_model):
        Config.configure_global_app(repository_type="sql")

        repository = _PipelineRepositoryFactory._build_repository()

        assert repository._to_model(pipeline) == pipeline_model
        assert repository._from_model(pipeline_model) == pipeline
