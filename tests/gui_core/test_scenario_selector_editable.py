# Copyright 2021-2025 Avaiga Private Limited
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
from unittest.mock import Mock

from taipy.gui import Gui
from taipy.gui_core._GuiCoreLib import _GuiCore


class TestScenarioSelectorEditable:
    """Test the editable property of scenario_selector visual element."""

    def test_scenario_selector_has_editable_property(self):
        """Test that scenario_selector element has editable property defined."""
        gui_core = _GuiCore()
        elements = gui_core.get_elements()
        
        assert "scenario_selector" in elements
        scenario_selector = elements["scenario_selector"]
        
        # Check that editable property exists in the element properties
        assert "editable" in scenario_selector.properties
        
        # Check that editable property has correct type and default value
        editable_prop = scenario_selector.properties["editable"]
        assert editable_prop.default_value is True
        assert str(editable_prop.type) == "PropertyType.dynamic_boolean"

    def test_scenario_selector_editable_default_true(self):
        """Test that editable property defaults to True."""
        gui_core = _GuiCore()
        elements = gui_core.get_elements()
        
        scenario_selector = elements["scenario_selector"]
        editable_prop = scenario_selector.properties["editable"]
        
        assert editable_prop.default_value is True

    def test_scenario_selector_editable_backward_compatibility(self):
        """Test that existing scenario_selector usage without editable prop still works."""
        gui_core = _GuiCore()
        elements = gui_core.get_elements()
        
        scenario_selector = elements["scenario_selector"]
        
        # Verify all existing properties are still present
        expected_properties = [
            "id", "show_add_button", "display_cycles", "show_primary_flag",
            "value", "on_change", "height", "class_name", "show_pins",
            "on_creation", "show_dialog", "scenarios", "multiple",
            "filter", "sort", "show_search", "editable"
        ]
        
        for prop in expected_properties:
            assert prop in scenario_selector.properties, f"Property {prop} missing from scenario_selector"

    def test_scenario_selector_editable_property_type(self):
        """Test that editable property has the correct type."""
        gui_core = _GuiCore()
        elements = gui_core.get_elements()
        
        scenario_selector = elements["scenario_selector"]
        editable_prop = scenario_selector.properties["editable"]
        
        # Should be dynamic boolean to allow state binding
        assert "dynamic_boolean" in str(editable_prop.type)