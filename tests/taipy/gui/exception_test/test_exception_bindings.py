# Copyright 2023 Avaiga Private Limited
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

from taipy.gui.utils._bindings import _Bindings


def test_exception_binding_twice(gui, test_client):
    bind = _Bindings(gui)
    bind._new_scopes()
    bind._bind("x", 10)
    with pytest.raises(ValueError):
        bind._bind("x", 10)


def test_exception_binding_invalid_name(gui):
    bind = _Bindings(gui)
    bind._new_scopes()
    with pytest.raises(ValueError):
        bind._bind("invalid identifier", 10)
