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

from taipy.common._repr_enum import _OrderedEnum


class SerializableObjectForTest(_OrderedEnum):
    FOO = 1
    BAR = 2

    @staticmethod
    def _type_identifier() -> str:
        return "SERIALIZABLE_OBJECT_FOR_TEST"

    def _stringify(self) -> str:
        return f"{self.name}:{self._type_identifier()}"

    @classmethod
    def _pythonify(cls, value: str):
        return SerializableObjectForTest[str.upper(value)]
