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
logging.basicConfig(level=logging.INFO)

lov = [("id1", "Menu option 1"), ("id2", "Menu option 2"), ("id3", "Menu option 3"), ("id4", "Menu option 4")]
selected_ids = ["id1", "id2"]

def menu_action(state, id, payload):
    active = payload.get("args")
    for i in active:
        logging.info(f"Menu option {i} selected")

md = """
<|menu|lov={lov}|selected_ids={selected_ids}|on_action=menu_action|>
"""

if __name__ == "__main__":
    Gui(md).run()
