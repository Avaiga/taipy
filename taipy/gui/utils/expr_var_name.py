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

import re
import typing as t

__expr_var_name_index: t.Dict[str, int] = {}
_RE_NOT_IN_VAR_NAME = r"[^A-Za-z0-9]+"


def _get_expr_var_name(expr: str) -> str:
    var_name = re.sub(_RE_NOT_IN_VAR_NAME, "_", expr)
    index = 0
    if var_name in __expr_var_name_index.keys():
        index = __expr_var_name_index[var_name]
    __expr_var_name_index[var_name] = index + 1
    return f"tp_{var_name}_{index}"


def _reset_expr_var_name():
    __expr_var_name_index.clear()
