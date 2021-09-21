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
