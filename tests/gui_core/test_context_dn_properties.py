# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
from unittest.mock import Mock, patch

from taipy.common.config.common.scope import Scope
from taipy.core.data.pickle import PickleDataNode
from taipy.gui_core._context import _GuiCoreContext

a_datanode = PickleDataNode("data_node_config_id", Scope.SCENARIO)


def mock_core_get(entity_id):
    if entity_id == a_datanode.id:
        return a_datanode
    return None

def mock_is_readable_false(entity_id):
    return False


def mock_is_true(entity_id):
    return True


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_data_node_properties:
    def test_get_data_node_properties(self):
        with (
            patch("taipy.gui_core._context.core_get", side_effect=mock_core_get),
            patch("taipy.gui_core._context.is_readable", side_effect=mock_is_true),
        ):
            gui_core_context = _GuiCoreContext(Mock())
            assert gui_core_context.get_data_node_properties("") is None
            assert gui_core_context.get_data_node_properties("not a datanode") is None
            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                assert gui_core_context.get_data_node_properties(a_datanode.id) is None
            assert gui_core_context.get_data_node_properties(a_datanode.id) is not None
            assert isinstance(gui_core_context.get_data_node_properties(a_datanode.id), list)
            assert len(t.cast(list, gui_core_context.get_data_node_properties(a_datanode.id))) == 0
