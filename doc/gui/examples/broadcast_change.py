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
# Demonstrate how to invoke a callback for different clients.
# This application creates a thread that, every second, invokes a callback for every client
# so the current time may be updated, under a state-dependant condition.
# -----------------------------------------------------------------------------------------
from datetime import datetime
from threading import Thread
from time import sleep

from taipy.gui import Gui

current_time = datetime.now()


# The function that executes in its own thread.
# Update the current time every second.
def update_time(gui):
    while True:
        gui.broadcast_change("current_time", datetime.now())
        sleep(1)


page = """
Current time is: <|{current_time}|format=HH:mm:ss|>
"""

gui = Gui(page)

# Run thread that regularly updates the current time
thread = Thread(target=update_time, args=[gui], name="clock")
thread.daemon = True
thread.start()

gui.run()
