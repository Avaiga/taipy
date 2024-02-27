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
import os
from pathlib import Path

from taipy.gui import Gui


def test_folder_pages_binding(gui: Gui):
    folder_path = f"{Path(Path(__file__).parent.resolve())}{os.path.sep}sample_assets"
    gui._set_frame(inspect.currentframe())
    gui.add_pages(folder_path)
    gui.run(run_server=False)
    assert len(gui._config.routes) == 3  # 2 files -> 2 routes + 1 default route
    assert len(gui._config.pages) == 3  # 2 files -> 2 pages + 1 default page
