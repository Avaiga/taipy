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
import logging

from taipy.gui import Gui

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

value = ""


# The [on_change] property is not set: Taipy GUI automatically finds and binds the global on_change()
# function to handle changes in the input control. You could set this property to your own function if necessary.
def on_change(state, var_name, v):
    logging.info(f"Value of {var_name} changed to {v}")


# If change_delay is set to -1, the change event is triggered on Enter key press
page = """
<|{value}|input|change_delay=-1|>
"""


if __name__ == "__main__":
    Gui(page).run(title="Input - on_change")
