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
# Demonstrate how to update the value of a variable across multiple clients.
# This application creates a thread that sets a variable to the current time.
# The value is updated for every client when Gui.broadcast_change() is invoked.
# -----------------------------------------------------------------------------------------
import asyncio

import taipy.gui.builder as tgb
from taipy.gui import Gui, State


# This callback is invoked inside a separate thread
# it can access the state but cannot return a value
async def heavy_function(state: State):
    state.logs = "Starting...\n"
    state.logs += "Searching documents\n"
    await asyncio.sleep(5)
    state.logs += "Responding to user\n"
    await asyncio.sleep(5)
    state.logs += "Fact Checking\n"
    await asyncio.sleep(5)
    state.result = "Done!"

logs = ""
result = "No response yet"

with tgb.Page() as main_page:
    # the async callback is used as any other callback
    tgb.button("Respond", on_action=heavy_function)
    with tgb.part("card"):
        tgb.text("{logs}", mode="pre")

    tgb.text("# Result", mode="md")
    tgb.text("{result}")


if __name__ == "__main__":
    Gui(main_page).run(title="Async - Callback")
