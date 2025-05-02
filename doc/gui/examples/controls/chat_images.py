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
# A chatting application based on the chat control.
# In order to see the users' avatars, the image files must be stored next to this script.
# If you want to test this application locally, you need to use several browsers and/or
# incognito windows so a given user's context is not reused.
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui, Icon

msgs = [
    ["1", "msg 1", "Alice", None],
    ["2", "msg From Another unknown User", "Charles", None],
    ["3", "This from the sender User", "taipy", "./beatrix-avatar.png"],
    ["4", "And from another known one", "Alice", None],
]
users = [
    ["Alice", Icon("./alice-avatar.png", "Alice avatar")],
    ["Charles", Icon("./charles-avatar.png", "Charles avatar")],
    ["taipy", Icon("./beatrix-avatar.png", "Beatrix avatar")],
]


def on_action(state, id: str, payload: dict):
    (reason, varName, text, senderId, imageData) = payload.get("args", [])
    msgs.append([f"{len(msgs) +1 }", text, senderId, imageData])
    state.msgs = msgs


page = """
<|{msgs}|chat|users={users}|allow_send_images|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chat - Images")
