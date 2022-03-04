from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_manager import PipelineManager


class TestPipelineRepository:
    def test_save_and_load(self, tmpdir, pipeline):
        repository = PipelineManager._repository
        repository.base_path = tmpdir
        repository.save(pipeline)
        loaded_pipeline = repository.load("pipeline_id")

        assert isinstance(loaded_pipeline, Pipeline)
        assert pipeline.id == loaded_pipeline.id

    def test_from_and_to_model(self, pipeline, pipeline_model):
        repository = PipelineManager._repository
        assert repository.to_model(pipeline) == pipeline_model
        assert repository.from_model(pipeline_model) == pipeline
