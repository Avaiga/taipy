class ModelNotFound(Exception):
    """
    Raised when trying to fetch a non existent model.
    """

    def __init__(self, model_name: str, model_id: str):
        self.message = f"A {model_name} model with id {model_id} could not be found."
