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
# Human-computer dialog UI based on the chat control.
# -----------------------------------------------------------------------------------------
from math import cos, pi, sin, sqrt, tan  # noqa: F401

from taipy.gui import Gui

# The user interacts with the Python interpretor
users = ["human", "Result"]
messages: list[tuple[str, str, str]] = []


def evaluate(state, var_name: str, payload: dict):
    # Retrieve the callback parameters
    (_, _, expression, sender_id) = payload.get("args", [])
    # Add the input content as a sent message
    messages.append((f"{len(messages)}", expression, sender_id))
    # Default message used if evaluation fails
    result = "Invalid expression"
    try:
        # Evaluate the expression and store the result
        result = f"= {eval(expression)}"
    except Exception:
        pass
    # Add the result as an incoming message
    messages.append((f"{len(messages)}", result, users[1]))
    state.messages = messages


page = """
# Taipy Calculator
<|toggle|theme|>

<|{messages}|chat|users={users}|sender_id={users[0]}|on_action=evaluate|>
"""

Gui(page).run()
