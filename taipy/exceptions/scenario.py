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
    """
    Raised when setting a scenario to be the master scenario but it doesn't belong to any cycle
    """

    pass


class DeletingMasterScenario(Exception):
    """
    Raised when trying to remove a master scenario
    """

    pass
