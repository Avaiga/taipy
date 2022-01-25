import pytest

from taipy.config import Config
from taipy.data import Scope


def test_scope():
    data_source_config_1 = Config.add_data_source("data_source_config_1", "in_memory", Scope.PIPELINE)
    data_source_config_2 = Config.add_data_source("data_source_config_2", "in_memory", Scope.SCENARIO)
    data_source_config_3 = Config.add_data_source("data_source_config_3", "in_memory", Scope.GLOBAL)
    data_source_config_4 = Config.add_data_source("data_source_config_4", "in_memory", Scope.PIPELINE)

    # Test __ge__ method
    assert data_source_config_2.scope >= data_source_config_1.scope
    assert data_source_config_2.scope >= data_source_config_2.scope
    assert data_source_config_1.scope >= data_source_config_4.scope
    with pytest.raises(TypeError):
        assert data_source_config_1.scope >= "testing string"

    # Test __gt__ method
    assert data_source_config_3.scope > data_source_config_1.scope
    assert data_source_config_3.scope > data_source_config_2.scope
    assert data_source_config_3.scope > data_source_config_4.scope
    with pytest.raises(TypeError):
        assert data_source_config_4.scope > "testing string"

    # Test __le__ method
    assert data_source_config_1.scope <= data_source_config_2.scope
    assert data_source_config_1.scope <= data_source_config_1.scope
    assert data_source_config_4.scope <= data_source_config_2.scope
    with pytest.raises(TypeError):
        assert data_source_config_1.scope <= "testing string"

    # Test __lt__ method
    assert data_source_config_1.scope < data_source_config_2.scope
    assert data_source_config_4.scope < data_source_config_2.scope
    assert data_source_config_2.scope < data_source_config_3.scope
    with pytest.raises(TypeError):
        assert data_source_config_1.scope < "testing string"
