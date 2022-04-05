# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pytest

from taipy.core.common.scope import Scope
from taipy.core.config.config import Config


def test_scope():
    data_node_config_1 = Config.configure_data_node("data_node_config_1", "in_memory", Scope.PIPELINE)
    data_node_config_2 = Config.configure_data_node("data_node_config_2", "in_memory", Scope.SCENARIO)
    data_node_config_3 = Config.configure_data_node("data_node_config_3", "in_memory", Scope.GLOBAL)
    data_node_config_4 = Config.configure_data_node("data_node_config_4", "in_memory", Scope.PIPELINE)

    # Test __ge__ method
    assert data_node_config_2.scope >= data_node_config_1.scope
    assert data_node_config_2.scope >= data_node_config_2.scope
    assert data_node_config_1.scope >= data_node_config_4.scope
    with pytest.raises(TypeError):
        assert data_node_config_1.scope >= "testing string"

    # Test __gt__ method
    assert data_node_config_3.scope > data_node_config_1.scope
    assert data_node_config_3.scope > data_node_config_2.scope
    assert data_node_config_3.scope > data_node_config_4.scope
    with pytest.raises(TypeError):
        assert data_node_config_4.scope > "testing string"

    # Test __le__ method
    assert data_node_config_1.scope <= data_node_config_2.scope
    assert data_node_config_1.scope <= data_node_config_1.scope
    assert data_node_config_4.scope <= data_node_config_2.scope
    with pytest.raises(TypeError):
        assert data_node_config_1.scope <= "testing string"

    # Test __lt__ method
    assert data_node_config_1.scope < data_node_config_2.scope
    assert data_node_config_4.scope < data_node_config_2.scope
    assert data_node_config_2.scope < data_node_config_3.scope
    with pytest.raises(TypeError):
        assert data_node_config_1.scope < "testing string"
