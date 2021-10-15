class NonExistingScenario(Exception):
    """
    Exception raised if we request a scenario not known by the scenario manager.
    """

    def __init__(self, scenario_id: str):
        self.message = f"Scenario : {scenario_id} does not exist."


class NonExistingScenarioConfig(Exception):
    """
    Exception raised if we request a scenario config not known by the scenario manager.
    """

    def __init__(self, scenario_config_name: str):
        self.message = f"Scenario config : {scenario_config_name} does not exist."
