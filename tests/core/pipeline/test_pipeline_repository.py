from taipy.core.pipeline._pipeline_manager import _PipelineManager
from taipy.core.pipeline.pipeline import Pipeline


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
