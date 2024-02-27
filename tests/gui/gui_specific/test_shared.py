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

from taipy.gui import Gui


def test_add_shared_variables(gui: Gui):
    Gui.add_shared_variable("var1", "var2")
    assert isinstance(gui._Gui__shared_variables, list)  # type: ignore[attr-defined]
    assert len(gui._Gui__shared_variables) == 2  # type: ignore[attr-defined]

    Gui.add_shared_variables("var1", "var2")
    assert len(gui._Gui__shared_variables) == 2  # type: ignore[attr-defined]
