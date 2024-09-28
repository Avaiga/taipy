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
import pandas as pd

from taipy.gui import Gui, State

categories = ["Real Estate", "Stocks", "Cash", "Retirement", "Other"]
amounts = [190000, 60000, 100000, 110000, 40000]


# Return an array where each item represents the percentage of the corresponding value in the
# input array:
# [10, 10] -> [50, 50]
# [1, 2, 3] -> [16, 33, 50]
def compute_ratio(amounts: list[int]) -> list[int]:
    total = sum(amounts)
    return [int((amount / total) * 100) for amount in amounts]


# Initialize the ratio array
ratio = compute_ratio(amounts)

# Create the dataset used by the table
data = pd.DataFrame({"Category": categories, "Amount": amounts, "%": ratio})


# Called when the user edits a cell's value
def update(state: State, var_name: str, payload: dict):
    # Batch the updates to the state
    with state:
        # Invoke the default processing for 'on_edit'
        # Because the table data is a Pandas data frame, the cell is updated automatically
        state.get_gui().table_on_edit(state, var_name, payload)
        # Update ratios based on the new cell value
        state.data["%"] = compute_ratio(state.data["Amount"])
        # Update the control
        state.refresh(var_name)


page = "<|{data}|table|editable[Amount]|on_edit=update|show_all|>"

if __name__ == "__main__":
    Gui(page).run(title="Table - Custom edit")
