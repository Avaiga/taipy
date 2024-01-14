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

_RE_MODULE = re.compile(r"^__(.*?)__$")


def _filter_locals(locals_dict: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {k: v for k, v in locals_dict.items() if (not _RE_MODULE.match(k) or k == "__name__")}
