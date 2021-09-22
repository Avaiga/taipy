class NonExistingDataSourceEntity(Exception):
    """
    Exception raised if we request a pipeline entity not known by the pipeline manager.
    """

    def __init__(self, scenario_id: str, data_source_name: str):
        self.message = f"No data source entity with name {data_source_name} contained in scenario entity {scenario_id}."


class NonExistingScenarioEntity(Exception):
    """
    Exception raised if we request a scenario entity not known by the scenario manager.
    """

    def __init__(self, scenario_id: str):
        self.message = f"Scenario entity : {scenario_id} does not exist."


class NonExistingScenario(Exception):
    """
    Exception raised if we request a scenario not known by the scenario manager.
    """

    def __init__(self, scenario_name: str):
        self.message = f"Scenario : {scenario_name} does not exist."
