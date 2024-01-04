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

import inspect
from time import sleep
from unittest.mock import patch

from taipy.gui import Gui, State, invoke_long_callback


def test_long_callback(gui: Gui):
    status = None  # noqa: F841

    def heavy_function(delay=1):
        sleep(delay)

    def heavy_function_with_exception(delay=1):
        sleep(delay)
        raise Exception("Heavy function Exception")

    def heavy_function_status(state: State, status: int):
        state.status = status

    def on_exception(state: State, function_name: str, e: Exception):
        state.status = -1

    gui._set_frame(inspect.currentframe())
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    state = gui._Gui__state

    with gui.get_flask_app().app_context():
        assert state.status is None
        invoke_long_callback(state, heavy_function)
        invoke_long_callback(state, heavy_function_with_exception)
        invoke_long_callback(state, heavy_function, (), heavy_function_status)
        invoke_long_callback(state, heavy_function, (2), heavy_function_status, (), 1000)
        invoke_long_callback(state, heavy_function_with_exception, (), heavy_function_status)
