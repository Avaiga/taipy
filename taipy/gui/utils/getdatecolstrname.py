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

_RE_PD_TYPE = re.compile(r"^([^\s\d\[]+)(\d+)(\[(.*,\s(\S+))\])?")


def _get_date_col_str_name(columns: t.List[str], col: str) -> str:
    suffix = "_str"
    while col + suffix in columns:
        suffix += "_"
    return col + suffix
