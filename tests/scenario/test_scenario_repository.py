from taipy.common.alias import ScenarioId
from taipy.scenario.manager import ScenarioManager
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel

scenario = Scenario("sc", [], {}, ScenarioId("sc_id"))

scenario_model = ScenarioModel(ScenarioId("sc_id"), "sc", [], {})


class TestScenarioRepository:
    def test_save_and_load(self, tmpdir):
        repository = ScenarioManager().repository
        repository.base_path = tmpdir
        repository.save(scenario)
        sc = repository.load("sc_id")

        assert isinstance(sc, Scenario)
        assert scenario.id == sc.id

    def test_from_and_to_model(self):
        repository = ScenarioManager().repository
        assert repository.to_model(scenario) == scenario_model
        assert repository.from_model(scenario_model) == scenario
