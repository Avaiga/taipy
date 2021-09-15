class NonExistingPipelineEntity(Exception):
    """
    Exception raised if we request a pipeline entity not known by the pipeline manager.
    """

    def __init__(self, pipeline_id: str):
        self.message = f"Pipeline entity : {pipeline_id} does not exist."


class NonExistingPipeline(Exception):
    """
    Exception raised if we request a pipeline not known by the task manager.
    """

    def __init__(self, pipeline_name: str):
        self.message = f"Pipeline : {pipeline_name} does not exist."
