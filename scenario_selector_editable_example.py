#!/usr/bin/env python3
"""
Example usage of scenario_selector with editable=False

This example demonstrates how to use the new editable property
to control whether users can edit scenario names and tags.
"""

from taipy.gui import Gui, Markdown, State
from taipy.core import Config, Scenario
from taipy.core.config import DataNodeConfig, TaskConfig, ScenarioConfig

# Configure a simple scenario for demonstration
input_cfg = DataNodeConfig("input", default_data="Hello World")
output_cfg = DataNodeConfig("output")

def process_data(input_data: str) -> str:
    return f"Processed: {input_data}"

task_cfg = TaskConfig("process", function=process_data, input=input_cfg, output=output_cfg)
scenario_cfg = ScenarioConfig("demo_scenario", task_configs=[task_cfg])

# State variables
selected_scenario = None
is_editable = True

def toggle_editable(state: State):
    """Toggle the editable state of the scenario selector."""
    state.is_editable = not state.is_editable

def on_scenario_change(state: State, var_name: str, value):
    """Handle scenario selection changes."""
    state.selected_scenario = value
    print(f"Selected scenario: {value.label if value else 'None'}")

# Page content demonstrating editable property
page_content = """
# Scenario Selector - Editable Property Demo

## Current Settings
- **Editable**: {is_editable}
- **Selected Scenario**: {selected_scenario.label if selected_scenario else "None"}

## Controls
<|Toggle Editable|button|on_action=toggle_editable|>

## Scenario Selector (Editable: {is_editable})
<|scenario_selector|value={selected_scenario}|editable={is_editable}|on_change=on_scenario_change|>

## Usage Notes

### When editable=True:
- Edit icons appear next to scenarios
- Users can modify scenario names and tags
- Full editing functionality available

### When editable=False:
- Edit icons are hidden
- Users cannot modify scenarios
- Selection, sorting, and adding still work
- Maintains all other functionality

### Example Code:
```python
# Read-only scenario selector
<|scenario_selector|editable=False|>

# Dynamic control with state variable
<|scenario_selector|editable={is_editable}|>

# Combined with other properties
<|scenario_selector|editable=False|show_add_button=True|show_search=True|>
```
"""

if __name__ == "__main__":
    # Create and run the GUI
    gui = Gui(Markdown(page_content))
    
    # Create some demo scenarios
    Config.configure_job_config(mode="standalone", nb_of_workers=1)
    
    # Run the application
    gui.run(title="Scenario Selector Editable Demo", port=5000)