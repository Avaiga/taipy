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
# The value is updated for every client in a function invoked by Gui.broadcast_change().
# The text of the button that starts or stops the thread is updated using the
# State.assign() method, and udateds on every client's browser because the variable was
# declared 'shared' by calling Gui.add_shared_variable().
# -----------------------------------------------------------------------------------------
from threading import Event, Thread
from time import sleep

from taipy.gui import Gui, State

counter = 0

# Thread management
thread = None
thread_event = Event()


def count(event, gui):
    while not event.is_set():
        global counter
        counter = counter + 1
        gui.broadcast_change("counter", counter)
        sleep(2)


# Start or stop the timer when the button is pressed
def start_or_stop(state: State):
    global thread
    if thread:  # Timer is running
        thread_event.set()
        thread = None
    else:  # Timer is stopped
        thread_event.clear()
        thread = Thread(target=count, args=[thread_event, state.get_gui()])
        thread.start()
    # Update button status for all states.
    state.assign("button_text", button_texts[1 if thread else 0])


button_texts = ["Start", "Stop"]
# Text in the start/stop button (initially "Start")
button_text = button_texts[0]

page = """
Counter: <|{counter}|>

Timer: <|{button_text}|button|on_action=start_or_stop|>
"""

if __name__ == "__main__":
    # Declare "button_text" as a shared variable.
    # Assigning a value to a state's 'button_text' property is propagated to all clients
    Gui.add_shared_variable("button_text")

    Gui(page).run(title="Broadcasting values")
