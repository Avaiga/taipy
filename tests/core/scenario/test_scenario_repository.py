from taipy.core.scenario._scenario_repository import _ScenarioRepository
from taipy.core.scenario.scenario import Scenario


def test_save_and_load(tmpdir, scenario):
    repository = _ScenarioRepository()
    repository.base_path = tmpdir
    repository._save(scenario)
    sc = repository.load(scenario.id)

    assert isinstance(sc, Scenario)
    assert scenario.id == sc.id


def test_from_and_to_model(scenario, scenario_model):
    repository = _ScenarioRepository()
    assert repository._to_model(scenario) == scenario_model
    assert repository._from_model(scenario_model) == scenario
