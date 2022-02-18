from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_repository import ScenarioRepository


def test_save_and_load(tmpdir, scenario):
    repository = ScenarioRepository()
    repository.base_path = tmpdir
    repository.save(scenario)
    sc = repository.load(scenario.id)

    assert isinstance(sc, Scenario)
    assert scenario.id == sc.id


def test_from_and_to_model(scenario, scenario_model):
    repository = ScenarioRepository()
    assert repository.to_model(scenario) == scenario_model
    assert repository.from_model(scenario_model) == scenario
