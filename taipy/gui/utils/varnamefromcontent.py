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

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from ..gui import Gui


def _varname_from_content(gui: Gui, content: str) -> t.Optional[str]:
    return next((k for k, v in gui._get_locals_bind().items() if isinstance(v, str) and v == content), None)
