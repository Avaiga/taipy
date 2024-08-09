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
from os import path
from typing import Union

from taipy.gui import Gui, Icon
from taipy.gui.gui_actions import navigate, notify

username = ""
users: list[Union[str, Icon]] = []
messages: list[tuple[str, str, str]] = []

Gui.add_shared_variables("messages", "users")


def on_init(state):
    # Copy the global variables users and messages to this user's state
    state.users = users
    state.messages = messages


def on_navigate(state, path: str):
    # Navigate to the 'register' page if the user is not registered
    if path == "discuss" and state.username == "":
        return "register"
    return path


def register(state):
    # Check that the user is not already registered
    for user in users:
        if state.username == user or (isinstance(user, (list, tuple)) and state.username == user[0]):
            notify(state, "error", "User already registered.")
            return
    # Use the avatar image if we can find it
    avatar_image_file = f"{state.username.lower()}-avatar.png"
    if path.isfile(avatar_image_file):
        users.append((state.username, Icon(avatar_image_file, state.username)))
    else:
        users.append(state.username)
    # Because users is a shared variable, this propagates to every client
    state.users = users
    navigate(state, "discuss")


def send(state, _: str, payload: dict):
    (_, _, message, sender_id) = payload.get("args", [])
    messages.append((f"{len(messages)}", message, sender_id))
    state.messages = messages


register_page = """
Please enter your user name:

<|{username}|input|>

<|Submit|button|on_action=register|>
"""

discuss_page = """
<|### Let's discuss, {username}|text|mode=markdown|>

<|{messages}|chat|users={users}|sender_id={username}|on_action=send|>
"""

pages = {"register": register_page, "discuss": discuss_page}
gui = Gui(pages=pages).run()
