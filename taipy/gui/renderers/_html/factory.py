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

import typing as t

from ..factory import _Factory


class _HtmlFactory(_Factory):
    @staticmethod
    def create_element(gui, control_type: str, all_properties: t.Dict[str, str]) -> t.Tuple[str, str]:
        builder = _Factory.CONTROL_BUILDERS[control_type](gui, control_type, all_properties)
        if not builder:
            return f"<div>INVALID SYNTAX - Control is '{control_type}'", "div"
        builder_str, element_name = builder.build_to_string()
        return builder_str, element_name
