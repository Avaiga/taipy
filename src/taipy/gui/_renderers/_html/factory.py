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

import typing as t

from ..factory import _Factory


class _HtmlFactory(_Factory):
    @staticmethod
    def create_element(gui, namespace: str, control_type: str, all_properties: t.Dict[str, str]) -> t.Tuple[str, str]:
        builder_html = _Factory.call_builder(gui, f"{namespace}.{control_type}", all_properties, True)
        if builder_html is None:
            return f"<div>INVALID SYNTAX - Control is '{namespace}:{control_type}'", "div"
        return builder_html  # type: ignore
