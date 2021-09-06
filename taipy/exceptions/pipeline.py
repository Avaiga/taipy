class NonExistingPipeline(Exception):
    """
    Exception raised if we request a pipeline not known by the task manager.
    """

    def __init__(self, pipeline_id: str):
        ...
        self.task_id = pipeline_id
        self.message = f"Pipeline : {pipeline_id} does not exist."
