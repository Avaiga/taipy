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

from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline.pipeline import Pipeline


class TestPipelineRepository:
    def test_save_and_load(self, tmpdir, pipeline):
        repository = _PipelineManager._repository
        repository.base_path = tmpdir
        repository._save(pipeline)
        loaded_pipeline = repository.load("pipeline_id")

        assert isinstance(loaded_pipeline, Pipeline)
        assert pipeline.id == loaded_pipeline.id

    def test_from_and_to_model(self, pipeline, pipeline_model):
        repository = _PipelineManager._repository
        assert repository._to_model(pipeline) == pipeline_model
        assert repository._from_model(pipeline_model) == pipeline
