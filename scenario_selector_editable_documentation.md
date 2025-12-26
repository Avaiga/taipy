# Scenario Selector - Editable Property

## Overview

The `scenario_selector` visual element now supports an optional `editable` argument that controls whether users can edit scenario names and tags.

## Property

### editable

- **Type**: `bool`
- **Default**: `True`
- **Dynamic**: Yes (can be bound to state variables)

When `editable=False`:
- Users cannot edit scenario names
- Users cannot edit scenario tags  
- The edit icon/button is hidden from the UI
- All other functionality remains available (selection, sorting, adding scenarios if `show_add_button=True`)

## Usage Examples

### Basic Usage - Disable Editing

```python
from taipy.gui import Gui, Markdown

# Disable editing for all scenarios
page = Markdown("""
<|scenario_selector|editable=False|>
""")

gui = Gui(page)
gui.run()
```

### Dynamic Control with State Variable

```python
from taipy.gui import Gui, Markdown, State

# Control editing through state variable
allow_editing = True

def toggle_editing(state: State):
    state.allow_editing = not state.allow_editing

page = Markdown("""
<|scenario_selector|editable={allow_editing}|>
<|Toggle Editing|button|on_action=toggle_editing|>
""")

gui = Gui(page)
gui.run()
```

### Combined with Other Properties

```python
from taipy.gui import Gui, Markdown

# Non-editable selector that still allows adding and searching
page = Markdown("""
<|scenario_selector|editable=False|show_add_button=True|show_search=True|>
""")

gui = Gui(page)
gui.run()
```

## Behavior

### When editable=True (default)
- Edit icons appear next to each scenario
- Users can click edit icons to modify scenario names and tags
- Full editing functionality is available
- Maintains backward compatibility with existing code

### When editable=False
- Edit icons are hidden from the UI
- Users cannot access scenario editing dialogs
- Selection, sorting, filtering, and searching still work normally
- Adding new scenarios still works if `show_add_button=True`

## Backward Compatibility

This change is fully backward compatible. Existing `scenario_selector` implementations will continue to work exactly as before, with editing enabled by default.

## Related Properties

The `editable` property works independently of other `scenario_selector` properties:

- `show_add_button`: Controls whether users can add new scenarios (independent of editing)
- `show_search`: Controls search functionality (independent of editing)  
- `filter` and `sort`: Control filtering and sorting (independent of editing)
- `multiple`: Controls multi-selection (independent of editing)

## Use Cases

1. **Read-only dashboards**: Display scenarios without allowing modifications
2. **Role-based access**: Disable editing for certain user roles while preserving other functionality
3. **Approval workflows**: Show scenarios in read-only mode during approval processes
4. **Audit views**: Display historical scenarios without edit capabilities