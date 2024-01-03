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

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, e2e_port, e2e_base_url):
    return {
        **browser_context_args,
        "base_url": f"http://127.0.0.1:{e2e_port}{e2e_base_url}",
        "timezone_id": "Europe/Paris",
    }


@pytest.fixture(scope="function")
def gui(helpers, e2e_base_url):
    from taipy.gui import Gui

    gui = Gui()
    gui.load_config({"base_url": e2e_base_url, "host": "0.0.0.0" if e2e_base_url != "/" else "127.0.0.1"})
    yield gui
    # Delete Gui instance and state of some classes after each test
    gui.stop()
    helpers.test_cleanup()
