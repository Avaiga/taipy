from taipy.pipeline import Pipeline, PipelineManager


class TestPipelineRepository:
    def test_save_and_load(self, tmpdir, pipeline):
        repository = PipelineManager().repository
        repository.base_path = tmpdir
        repository.save(pipeline)
        pi = repository.load("pipeline_id")

        assert isinstance(pi, Pipeline)
        assert pipeline.id == pi.id

    def test_from_and_to_model(self, pipeline, pipeline_model):
        repository = PipelineManager().repository
        assert repository.to_model(pipeline) == pipeline_model
        assert repository.from_model(pipeline_model) == pipeline
