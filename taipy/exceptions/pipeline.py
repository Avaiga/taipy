class NonExistingPipeline(Exception):
    """
    Exception raised if we request a pipeline not known by the pipeline manager.
    """

    def __init__(self, pipeline_id: str):
        self.message = f"Pipeline : {pipeline_id} does not exist."


class NonExistingPipelineConfig(Exception):
    """
    Exception raised if we request a pipeline not known by the pipeline manager.
    """

    def __init__(self, pipeline_config_name: str):
        self.message = f"Pipeline config : {pipeline_config_name} does not exist."
