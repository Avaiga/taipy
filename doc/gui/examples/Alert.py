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
from taipy.gui import Gui

# Initial dynamic properties
severity = "error"
variant = "filled"
message = "This is an error message."
render = True

# A simple page that binds the Alert component to dynamic variables and adds a button to trigger the update
page = """
<|{message}|alert|severity={severity}|variant={variant}|render={render}|>
<br/>
<|Update Alert|button|on_action=update_alert|>
"""

# Function to toggle between variants and severities
def update_alert(state):
    severities = ["error", "warning", "info", "success"]
    variants = ["filled", "outlined"]
    
    state.severity = random.choice(severities)
    state.variant = random.choice(variants)
    state.message = f"This is a {state.severity} message with {state.variant} variant."

if __name__ == "__main__":
    gui = Gui(page)
    gui.run(title="Test Alert")