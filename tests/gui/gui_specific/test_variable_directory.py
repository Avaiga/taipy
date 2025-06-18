# Copyright 2021-2025 Avaiga Private Limited
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
from taipy.gui.utils import _LocalsContext, _VariableDirectory

from .state_asset.page1 import md_page1
from .state_asset.page2 import md_page2


def test_variable_directory_dynamic_process(gui: Gui):
    gui.run(run_server=False)
    with gui.get_app_context():
        locals_context = _LocalsContext(gui)
        variable_directory = _VariableDirectory(locals_context)
        page1_module = str(md_page1._get_module_name())
        page2_module = str(md_page2._get_module_name())
        locals_context.add(page1_module, md_page1._get_locals())
        variable_directory.set_default(md_page1._get_frame())  # type: ignore
        variable_directory.process_imported_var()
        assert page1_module in variable_directory._pre_processed_module
        assert page1_module in variable_directory._processed_module
        locals_context.add(page2_module, md_page2._get_locals())
        variable_directory.add_frame(md_page2._get_frame())
        variable_directory.process_imported_var()
        assert page2_module in variable_directory._pre_processed_module
        assert page2_module in variable_directory._processed_module
