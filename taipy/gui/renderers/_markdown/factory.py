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

from ..factory import _Factory


class _MarkdownFactory(_Factory):
    # Taipy Markdown tags
    _TAIPY_START = "TaIpY:"
    _TAIPY_END = ":tAiPy"

    _TAIPY_BLOCK_TAGS = ["layout", "part", "expandable", "dialog", "pane"]

    @staticmethod
    def create_element(gui, control_type: str, all_properties: str) -> str:
        # Create properties dict from all_properties
        property_pairs = _Factory._PROPERTY_RE.findall(all_properties)
        properties = {property[0]: property[1] for property in property_pairs}
        if builder := _Factory.CONTROL_BUILDERS[control_type](gui, control_type, properties):
            return builder.el
        else:
            return f"<|INVALID SYNTAX - Control is '{control_type}'|>"
