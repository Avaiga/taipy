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
import taipy.gui.builder as tgb
from taipy.gui import Gui

show_dialog = False


def dialog_action(state, _, payload):
    if payload["args"][0] == 0:  # First button
        print("Good to hear!")  # noqa: T201
    elif payload["args"][0] == 1:  # Second button
        print("Sorry to hear that.")  # noqa: T201
    else:  # Close button (index == -1)
        print("Ok bye.")  # noqa: T201
    state.show_dialog = False


with tgb.Page() as page:
    with tgb.dialog("{show_dialog}", title="Welcome!", on_action=dialog_action, labels="Couldn't be better;Not my day"):  # type: ignore
        tgb.html("h2", "Hello!")

    tgb.button("Show", on_action=lambda s: s.assign("show_dialog", True))

if __name__ == "__main__":
    Gui(page).run(title="Dialog - Labels")
