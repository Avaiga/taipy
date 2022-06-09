# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from importlib.util import find_spec

if find_spec('taipy.core'):
    from taipy.core import *

if find_spec('taipy.gui'):
    from taipy.gui import Gui

    if find_spec('taipy.enterprise') and find_spec('taipy.enterprise.gui'):
        from taipy.enterprise.gui import _init_gui_enterprise

        _init_gui_enterprise(Gui)

if find_spec('taipy.rest'):
    from taipy.rest import Rest

if find_spec('taipy._run'):
    from taipy._run import _run as run
