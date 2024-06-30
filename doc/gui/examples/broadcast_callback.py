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
from datetime import datetime
from threading import Thread
from time import sleep

from taipy.gui import Gui

current_time = datetime.now()
update = False

# Update the 'current_time' state variable if 'update' is True
def update_state(state, updated_time):
    if state.update:
        state.current_time = updated_time

# The function that executes in its own thread.
# Call 'update_state()` every second.
def update_time(gui):
    while True:
        gui.broadcast_callback(update_state, [datetime.now()])
        sleep(1)

page = """
Current time is: <|{current_time}|format=HH:mm:ss|>

Update: <|{update}|toggle|>
"""

gui = Gui(page)

# Run thread that regularly updates the current time
thread = Thread(target=update_time, args=[gui], name="clock")
thread.daemon = True
thread.start()

gui.run()
