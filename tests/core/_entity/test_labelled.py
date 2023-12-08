# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from unittest import mock

import pytest
from taipy.config import Config, Frequency, Scope
from taipy.core import taipy
from taipy.core._entity._labeled import _Labeled


class MockOwner:
    label = "owner_label"

    def get_label(self):
        return self.label


def test_get_label():
    labeled_entity = _Labeled()

    with pytest.raises(NotImplementedError):
        labeled_entity.get_label()

    with pytest.raises(NotImplementedError):
        labeled_entity.get_simple_label()

    with pytest.raises(AttributeError):
        labeled_entity._get_label()

    with pytest.raises(AttributeError):
        labeled_entity._get_simple_label()

    labeled_entity.id = "id"
    assert labeled_entity._get_label() == "id"
    assert labeled_entity._get_simple_label() == "id"

    labeled_entity.config_id = "the config id"
    assert labeled_entity._get_label() == "the config id"
    assert labeled_entity._get_simple_label() == "the config id"

    labeled_entity._properties = {"name": "a name"}
    assert labeled_entity._get_label() == "a name"
    assert labeled_entity._get_simple_label() == "a name"

    labeled_entity.owner_id = "owner_id"
    with mock.patch("taipy.core.get") as get_mck:
        get_mck.return_value = MockOwner()
        assert labeled_entity._get_label() == "owner_label > a name"
        assert labeled_entity._get_simple_label() == "a name"

        labeled_entity._properties["label"] = "a wonderful label"
        assert labeled_entity._get_label() == "a wonderful label"
        assert labeled_entity._get_simple_label() == "a wonderful label"


def mult(n1, n2):
    return n1 * n2


def test_get_label_complex_case():
    dn1_cfg = Config.configure_data_node("dn1", scope=Scope.GLOBAL)
    dn2_cfg = Config.configure_data_node("dn2", scope=Scope.CYCLE)
    dn3_cfg = Config.configure_data_node("dn3", scope=Scope.CYCLE)
    dn4_cfg = Config.configure_data_node("dn4", scope=Scope.SCENARIO)
    dn5_cfg = Config.configure_data_node("dn5", scope=Scope.SCENARIO)
    tA_cfg = Config.configure_task("t_A_C", mult, [dn1_cfg, dn2_cfg], dn3_cfg)
    tB_cfg = Config.configure_task("t_B_S", mult, [dn3_cfg, dn4_cfg], dn5_cfg)
    scenario_cfg = Config.configure_scenario("scenario_cfg", [tA_cfg, tB_cfg], [], Frequency.DAILY)
    scenario_cfg.add_sequences(
        {
            "sequence_C": [tA_cfg],
            "sequence_S": [tA_cfg, tB_cfg],
        }
    )

    scenario = taipy.create_scenario(scenario_cfg, name="My Name")
    cycle = scenario.cycle
    cycle.name = "Today"
    sequence_C = scenario.sequence_C
    sequence_S = scenario.sequence_S
    tA = scenario.t_A_C
    tB = scenario.t_B_S
    dn1 = scenario.dn1
    dn2 = scenario.dn2
    dn3 = scenario.dn3
    dn4 = scenario.dn4
    dn5 = scenario.dn5

    assert cycle.get_label() == scenario.cycle.name
    assert cycle.get_simple_label() == scenario.cycle.name
    assert scenario.get_label() == "Today > My Name"
    assert scenario.get_simple_label() == "My Name"
    assert sequence_C.get_label() == "Today > My Name > sequence_C"
    assert sequence_C.get_simple_label() == "sequence_C"
    assert sequence_S.get_label() == "Today > My Name > sequence_S"
    assert sequence_S.get_simple_label() == "sequence_S"
    assert tA.get_label() == "Today > t_A_C"
    assert tA.get_simple_label() == "t_A_C"
    assert tB.get_label() == "Today > My Name > t_B_S"
    assert tB.get_simple_label() == "t_B_S"
    assert dn1.get_label() == "dn1"
    assert dn1.get_simple_label() == "dn1"
    assert dn2.get_label() == "Today > dn2"
    assert dn2.get_simple_label() == "dn2"
    assert dn3.get_label() == "Today > dn3"
    assert dn3.get_simple_label() == "dn3"
    assert dn4.get_label() == "Today > My Name > dn4"
    assert dn4.get_simple_label() == "dn4"
    assert dn5.get_label() == "Today > My Name > dn5"
    assert dn5.get_simple_label() == "dn5"
