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

from ._attributes import (
    _delscopeattr,
    _getscopeattr,
    _getscopeattr_drill,
    _hasscopeattr,
    _setscopeattr,
    _setscopeattr_drill,
)
from ._locals_context import _LocalsContext
from ._map_dict import _MapDict
from ._runtime_manager import _RuntimeManager
from ._variable_directory import _variable_decode, _variable_encode, _VariableDirectory
from .boolean import _is_boolean, _is_boolean_true
from .clientvarname import _get_broadcast_var_name, _get_client_var_name, _to_camel_case
from .datatype import _get_data_type
from .date import _date_to_string, _string_to_date
from .expr_var_name import _get_expr_var_name
from .filename import _get_non_existent_file_path
from .filter_locals import _filter_locals
from .get_imported_var import _get_imported_var
from .get_module_name import _get_module_name_from_frame, _get_module_name_from_imported_var
from .get_page_from_module import _get_page_from_module
from .getdatecolstrname import _RE_PD_TYPE, _get_date_col_str_name
from .html import _get_css_var_value
from .is_debugging import is_debugging
from .isnotebook import _is_in_notebook
from .types import (
    _TaipyBase,
    _TaipyBool,
    _TaipyContent,
    _TaipyContentImage,
    _TaipyData,
    _TaipyDate,
    _TaipyDict,
    _TaipyLoNumbers,
    _TaipyLov,
    _TaipyLovValue,
    _TaipyNumber,
)
from .varnamefromcontent import _varname_from_content
