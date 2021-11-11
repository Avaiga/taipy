from taipy.cycle.cycle import Cycle
from taipy.cycle.repository import CycleRepository


def test_save_and_load(tmpdir, cycle):
    repository = CycleRepository()
    repository.base_path = tmpdir
    repository.save(cycle)
    cc = repository.load(cycle.id)

    assert isinstance(cc, Cycle)
    assert cc.id == cycle.id
    assert cc.name == cycle.name
    assert cc.creation_date == cycle.creation_date


def test_from_and_to_model(cycle, cycle_model):
    repository = CycleRepository()
    assert repository.to_model(cycle) == cycle_model
    assert repository.from_model(cycle_model) == cycle
