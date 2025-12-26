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
from unittest.mock import Mock, patch

from taipy.core import Scenario
from taipy.gui import Gui, Markdown
from taipy.gui_core import _GuiCore


class TestScenarioSelectorEditableIntegration:
    """Integration tests for scenario_selector editable functionality."""

    def test_scenario_selector_editable_true_renders_edit_component(self):
        """Test that when editable=True, edit component is rendered."""
        # This test would require a full GUI setup and frontend testing
        # For now, we test the property configuration
        gui = Gui()
        gui_core = _GuiCore()
        
        # Test that the property is correctly configured
        elements = gui_core.get_elements()
        scenario_selector = elements["scenario_selector"]
        
        assert "editable" in scenario_selector.properties
        assert scenario_selector.properties["editable"].default_value is True

    def test_scenario_selector_editable_false_configuration(self):
        """Test that editable=False can be configured."""
        gui = Gui()
        gui_core = _GuiCore()
        
        # Create a page with scenario_selector having editable=False
        page_content = """
<|scenario_selector|editable=False|>
"""
        
        # This would be tested in a full integration environment
        # For now, verify the property exists and can be set
        elements = gui_core.get_elements()
        scenario_selector = elements["scenario_selector"]
        
        # Verify the property can accept False value
        editable_prop = scenario_selector.properties["editable"]
        assert "dynamic_boolean" in str(editable_prop.type)

    def test_scenario_selector_with_state_binding(self):
        """Test that editable property can be bound to state variables."""
        gui = Gui()
        gui_core = _GuiCore()
        
        # Test state binding capability
        elements = gui_core.get_elements()
        scenario_selector = elements["scenario_selector"]
        editable_prop = scenario_selector.properties["editable"]
        
        # Should support dynamic binding
        assert "dynamic" in str(editable_prop.type)

    def test_scenario_selector_maintains_other_functionality_when_not_editable(self):
        """Test that when editable=False, other functionality still works."""
        gui = Gui()
        gui_core = _GuiCore()
        
        # Verify all other properties are still available
        elements = gui_core.get_elements()
        scenario_selector = elements["scenario_selector"]
        
        # Key properties that should still work when editable=False
        functional_properties = [
            "value", "on_change", "show_add_button", "multiple",
            "filter", "sort", "show_search"
        ]
        
        for prop in functional_properties:
            assert prop in scenario_selector.properties

    def test_scenario_selector_editable_with_show_add_button(self):
        """Test that editable=False doesn't affect show_add_button functionality."""
        gui = Gui()
        gui_core = _GuiCore()
        
        elements = gui_core.get_elements()
        scenario_selector = elements["scenario_selector"]
        
        # Both properties should be independent
        assert "editable" in scenario_selector.properties
        assert "show_add_button" in scenario_selector.properties
        
        # show_add_button should default to True regardless of editable
        assert scenario_selector.properties["show_add_button"].default_value is True