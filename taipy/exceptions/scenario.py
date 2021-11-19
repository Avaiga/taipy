class NonExistingScenario(Exception):
    """
    Raised when a requested scenario is not known by the Scenario Manager.
    """

    def __init__(self, scenario_id: str):
        self.message = f"Scenario: {scenario_id} does not exist."


class NonExistingScenarioConfig(Exception):
    """
    Raised when a requested scenario configuration is not known by the Scenario Manager.
    """

    def __init__(self, scenario_config_name: str):
        self.message = f"Scenario config: {scenario_config_name} does not exist."


class DoesNotBelongToACycle(Exception):
    pass
