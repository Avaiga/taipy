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
# Demonstrate how to share variable values across multiple clients.
# This application creates a thread that increments a value every few seconds.
# The value is updated for every client using the state.broadcast() method.
# The text of the button that starts or stops the thread is updated on every client's browser
# using a direct assignment of the state property because the variable is declared 'shared'.
# -----------------------------------------------------------------------------------------
from threading import Event, Thread
from time import sleep

from taipy.gui import Gui, State, broadcast_callback

counter = 0

# Thread management
thread = None
thread_event = Event()

button_texts = ["Start", "Stop"]
# Text in the start/stop button (initially "Start")
button_text = button_texts[0]


# Invoked by the timer
def update_counter(state: State, c):
    # Update all clients
    state.broadcast("counter", c)


def count(event, gui):
    while not event.is_set():
        global counter
        counter = counter + 1
        broadcast_callback(gui, update_counter, [counter])
        sleep(2)


# Start or stop the timer when the button is pressed
def start_or_stop(state):
    global thread
    if thread:  # Timer is running
        thread_event.set()
        thread = None
    else:  # Timer is stopped
        thread_event.clear()
        thread = Thread(target=count, args=[thread_event, state.get_gui()])
        thread.start()
    # Update button status.
    # Because "button_text" is shared, all clients are updated
    state.button_text = button_texts[1 if thread else 0]


page = """# Broadcasting values

Counter: <|{counter}|>

Timer: <|{button_text}|button|on_action=start_or_stop|>
"""

# Declare "button_text" as a shared variable.
# Assigning a value to a state's 'button_text' property is propagated to all clients
Gui.add_shared_variable("button_text")

Gui(page).run()
