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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python state_patch_demo.py
# -----------------------------------------------------------------------------------------
"""
Demonstrates the State.patch method for efficient partial updates of complex data structures.

This example shows how to use state.patch() to update dictionaries, lists, and nested
structures without replacing the entire variable, which is more efficient for large
data structures and provides better user experience.
"""

from taipy.gui import Gui, Markdown

# Initial application data
app_data = {
    "user": {"name": "John Doe", "age": 30, "email": "john@example.com"},
    "tasks": [
        {"id": 1, "title": "Learn Taipy", "completed": False},
        {"id": 2, "title": "Build an app", "completed": False},
        {"id": 3, "title": "Deploy to production", "completed": False}
    ],
    "settings": {"theme": "light", "notifications": True, "language": "en"}
}

# Counter for generating new task IDs
next_task_id = 4


def update_user_age(state):
    """Demonstrate updating a nested dictionary value."""
    state.patch("app_data", change={"user": {"age": state.app_data["user"]["age"] + 1}})


def update_user_email(state):
    """Demonstrate updating a specific key in a nested structure."""
    new_email = f"updated_{state.app_data['user']['name'].lower().replace(' ', '.')}@company.com"
    state.patch("app_data", change={"user": {"email": new_email}})


def toggle_task_completion(state, task_index: int):
    """Demonstrate updating an object within a list."""
    current_status = state.app_data["tasks"][task_index]["completed"]
    state.patch("app_data", change={
        "tasks": {task_index: {"completed": not current_status}}
    })


def add_new_task(state):
    """Demonstrate appending to a list using patch."""
    global next_task_id
    new_task = {"id": next_task_id, "title": f"New Task {next_task_id}", "completed": False}
    # Use a large index to append to the end
    state.patch("app_data", change={"tasks": {1000: [new_task]}})
    next_task_id += 1


def insert_urgent_task(state):
    """Demonstrate inserting at the beginning of a list."""
    global next_task_id
    urgent_task = {"id": next_task_id, "title": "URGENT: Fix critical bug", "completed": False}
    # Use negative index to insert at the beginning
    state.patch("app_data", change={"tasks": {-1: [urgent_task]}})
    next_task_id += 1


def remove_completed_tasks(state):
    """Demonstrate removing items from a list."""
    # Find completed tasks and remove them (iterate backwards to avoid index shifts)
    for i in range(len(state.app_data["tasks"]) - 1, -1, -1):
        if state.app_data["tasks"][i]["completed"]:
            state.patch("app_data", remove={"tasks": {i: None}})


def toggle_theme(state):
    """Demonstrate updating a simple dictionary value."""
    current_theme = state.app_data["settings"]["theme"]
    new_theme = "dark" if current_theme == "light" else "light"
    state.patch("app_data", change={"settings": {"theme": new_theme}})


def reset_data(state):
    """Reset to original data structure."""
    global next_task_id
    state.app_data = {
        "user": {"name": "John Doe", "age": 30, "email": "john@example.com"},
        "tasks": [
            {"id": 1, "title": "Learn Taipy", "completed": False},
            {"id": 2, "title": "Build an app", "completed": False},
            {"id": 3, "title": "Deploy to production", "completed": False}
        ],
        "settings": {"theme": "light", "notifications": True, "language": "en"}
    }
    next_task_id = 4


# Task completion buttons
def complete_task_0(state):
    toggle_task_completion(state, 0)

def complete_task_1(state):
    toggle_task_completion(state, 1)

def complete_task_2(state):
    toggle_task_completion(state, 2)


# Define the main page layout
page = Markdown("""
# State.patch() Demonstration

This demo shows various uses of the `state.patch()` method for efficient partial updates.

## User Information
**Name:** {app_data[user][name]}  
**Age:** {app_data[user][age]}  
**Email:** {app_data[user][email]}

<|Increase Age|button|on_action=update_user_age|>
<|Update Email|button|on_action=update_user_email|>

## Tasks
{app_data[tasks]}

### Task Actions
<|Toggle Task 1|button|on_action=complete_task_0|>
<|Toggle Task 2|button|on_action=complete_task_1|>
<|Toggle Task 3|button|on_action=complete_task_2|>

<|Add New Task|button|on_action=add_new_task|>
<|Insert Urgent Task|button|on_action=insert_urgent_task|>
<|Remove Completed|button|on_action=remove_completed_tasks|>

## Settings
**Theme:** {app_data[settings][theme]}  
**Notifications:** {app_data[settings][notifications]}  
**Language:** {app_data[settings][language]}

<|Toggle Theme|button|on_action=toggle_theme|>

## Reset
<|Reset All Data|button|on_action=reset_data|>

---

## About state.patch()

The `state.patch()` method allows you to update only specific parts of your data structures
instead of replacing entire variables. This is especially useful for:

- **Performance**: Only the changed parts are updated in the UI
- **Network efficiency**: Smaller updates are sent to the client
- **User experience**: Reduces flicker and maintains UI state
- **Complex data**: Safely update nested structures without affecting other parts

### Key Benefits Demonstrated:

1. **Dictionary updates**: Changing user age/email without affecting other user properties
2. **List operations**: Adding, removing, and modifying tasks in the task list
3. **Nested updates**: Updating specific properties of objects within lists
4. **Efficient insertions**: Adding items at specific positions or at the end
""")

if __name__ == "__main__":
    Gui(page).run(title="State.patch() Demo", debug=True)