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
from taipy.gui import Gui

init_value = ""


def print_value_on_key_pressed(state, id, payload):
    key = payload.get('args', [None])[0]
    if key == 'F1':
        print("F1 key pressed")
    elif key == 'F2':
        print("F2 key pressed")
    elif key == 'F3':
        print("F3 key pressed")
    else:
        return None


# on_action function is called when the action_keys are pressed
page = """
Enter a number (on_action triggered on F1, F2, F3 key press): 
<|{init_value}|input|change_delay=300|on_action=print_value_on_key_pressed|action_keys=F1;F2;F3|>
"""

if __name__ == "__main__":
    Gui(page).run()