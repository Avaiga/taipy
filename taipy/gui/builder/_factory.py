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

import typing as t

from .._renderers.factory import _Factory


class _BuilderFactory(_Factory):
    @staticmethod
    def create_element(gui, element_type: str, properties: t.Dict[str, t.Any]) -> t.Tuple[str, str]:
        builder_html = _Factory.call_builder(gui, element_type, properties, True)
        if builder_html is None:
            return f"<div>INVALID SYNTAX - Element is '{element_type}'", "div"
        return builder_html  # type: ignore
