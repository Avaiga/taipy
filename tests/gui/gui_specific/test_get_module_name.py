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

from taipy.gui.utils.get_module_name import _get_module_name_from_frame, _get_module_name_from_imported_var

x = 10


def test_get_module_name():
    assert "tests.gui.gui_specific.test_get_module_name" == _get_module_name_from_frame(inspect.currentframe())


def test_get_module_name_imported_var():
    assert "tests.gui.gui_specific.test_get_module_name" == _get_module_name_from_imported_var(
        "x", 10, "test_get_module_name"
    )
    assert "test_get_module_name" == _get_module_name_from_imported_var("x", 11, "test_get_module_name")
