from taipy.common.alias import ScenarioId
from taipy.scenario.manager import ScenarioManager
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel


class TestScenarioRepository:
    def test_save_and_load(self, tmpdir, scenario_entity):
        repository = ScenarioManager().repository
        repository.base_path = tmpdir
        repository.save(scenario_entity)
        sc = repository.load("sc_id")

        assert isinstance(sc, Scenario)
        assert scenario_entity.id == sc.id

    def test_from_and_to_model(self, scenario_entity, scenario_model):
        repository = ScenarioManager().repository
        assert repository.to_model(scenario_entity) == scenario_model
        assert repository.from_model(scenario_model) == scenario_entity
