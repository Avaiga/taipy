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

import enum
import json
from typing import Any, Dict

from sqlalchemy import Table

from ._decoder import _Decoder
from ._encoder import _Encoder


class _BaseModel:
    __table__: Table

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def to_dict(self) -> Dict[str, Any]:
        model_dict = {**self.__dict__}

        for k, v in model_dict.items():
            if isinstance(v, enum.Enum):
                model_dict[k] = repr(v)
        return model_dict

    @staticmethod
    def _serialize_attribute(value):
        return json.dumps(value, ensure_ascii=False, cls=_Encoder)

    @staticmethod
    def _deserialize_attribute(value):
        if isinstance(value, str):
            return json.loads(value.replace("'", '"'), cls=_Decoder)
        return value

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        pass

    def to_list(self):
        pass
