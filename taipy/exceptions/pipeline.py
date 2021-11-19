class NonExistingPipeline(Exception):
    """
    Raised if a requested Pipeline is not known by the Pipeline Manager.
    """

    def __init__(self, pipeline_id: str):
        self.message = f"Pipeline: {pipeline_id} does not exist."


class NonExistingPipelineConfig(Exception):
    """
    Raised if a requested Pipeline configuration is not known by the Pipeline Manager.
    """

    def __init__(self, pipeline_config_name: str):
        self.message = f"Pipeline config: {pipeline_config_name} does not exist."
