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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
import random

import requests

from taipy.gui import Gui, State, notify

# The RandomAPI API used to generate random user names
randomuser_url = "https://randomuser.me/api"


# Create a random person name and salary
def pick_user() -> tuple[str, int]:
    # Call the Random User Generator API to create a random person name
    response = requests.get(randomuser_url)
    # If the request was successful
    if response.status_code == 200:
        # Make a new name and
        try:
            person = response.json()["results"][0]
            name = person["name"]
            new_user = f"{name["first"]} {name["last"]}"
            # Generate a random salary expectation amount
            salary = random.randint(8, 24) * 5000
            return (new_user, salary)
        except ValueError:
            # There was a back-end error
            print("ERROR: Invoking the Random User Generator API")  # noqa: F401, T201
            return ("ERROR", 0)
    # The API cannot be reached
    print("ERROR: Could not invoke the Random User Generator API")  # noqa: F401, T201
    return ("ERROR", 0)


# Generate four random persons with their salary expectation and store them in a dictionary
candidates: dict[str, list] = {"Name": [], "Salary": []}
for candidate in [pick_user() for _ in range(4)]:
    candidates["Name"].append(candidate[0])
    candidates["Salary"].append(candidate[1])


# Triggered when the user clicks the 'Delete' icon and validates
def check_delete(state: State, var_name: str, payload: dict):
    # How many candidates are there in the list? (i.e. how many rows in the table)
    n_candidates = len(state.candidates["Name"])
    # Check if a candidate can be removed from the list
    if n_candidates <= 3:
        # Notify the user that the minimum limit has been reached
        notify(state, "E", "Too few candidates")
    else:
        # Remove the row from the table
        state.get_gui().table_on_delete(state, var_name, payload)


# Triggered when the user clicks the 'Add' icon and validates
def check_add(state: State, var_name: str, payload: dict):
    # How many candidates are there in the list? (i.e. how many rows in the table)
    n_candidates = len(state.candidates["Name"])
    # Check if a new candidate can be added to the list
    if n_candidates >= 6:
        # Notify the user that the maximum limit has been reached
        notify(state, "E", "Too many candidates")
    else:
        # Create new candidate
        new_row = pick_user()
        # Add new row at the end of the list
        payload["index"] = n_candidates
        # Add the new candidate as a row in the table
        state.get_gui().table_on_add(state, var_name, payload, new_row=list(new_row))


# Triggered when the user changes the value of a cell
# Force the user-entered value to be a multiple of 5000
def force_salary(state: State, var_name: str, payload: dict):
    # Get the salary proposal from the callback's payload
    proposed_salary = payload["value"]
    # Round it the the nearest multiple of 5000
    proposed_salary = round(proposed_salary / 500) * 500
    # Set it as the value to be stored in the dataset
    payload["value"] = proposed_salary
    state.get_gui().table_on_edit(state, var_name, payload)


page = "<|{candidates}|table|on_delete=check_delete|on_add=check_add|editable[Salary]|on_edit=force_salary|show_all|>"

if __name__ == "__main__":
    Gui(page).run(title="Table - Guard edits")
