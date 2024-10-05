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

from typing import Any, Callable, Dict, List, Union

import numpy as np
import pandas as pd

from ..exceptions.exceptions import InvalidExposedType


class _TabularDataNodeMixin(object):
    """Mixin class designed to handle tabular representable data nodes."""

    _HAS_HEADER_PROPERTY = "has_header"
    _EXPOSED_TYPE_PROPERTY = "exposed_type"
    _EXPOSED_TYPE_NUMPY = "numpy"
    _EXPOSED_TYPE_PANDAS = "pandas"
    _EXPOSED_TYPE_MODIN = "modin"  # Deprecated in favor of pandas since 3.1.0
    _VALID_STRING_EXPOSED_TYPES = [_EXPOSED_TYPE_PANDAS, _EXPOSED_TYPE_NUMPY]

    def __init__(self, **kwargs) -> None:
        self._decoder: Union[Callable, Any]
        self.custom_document = kwargs.get(self._EXPOSED_TYPE_PROPERTY)

        custom_decoder = getattr(self.custom_document, "decode", None)
        if callable(custom_decoder):
            self._decoder = custom_decoder
        elif kwargs.get(self._HAS_HEADER_PROPERTY, True):
            self._decoder = self._default_decoder_with_header
        else:
            self._decoder = self._default_decoder_without_header

        self._encoder = self._default_encoder
        custom_encoder = getattr(self.custom_document, "encode", None)
        if callable(custom_encoder):
            self._encoder = custom_encoder


    def _convert_data_to_dataframe(self, exposed_type: Any, data: Any) -> Union[pd.DataFrame, pd.Series]:
        if exposed_type == self._EXPOSED_TYPE_PANDAS and isinstance(data, (pd.DataFrame, pd.Series)):
            return data
        elif exposed_type == self._EXPOSED_TYPE_NUMPY and isinstance(data, np.ndarray):
            return pd.DataFrame(data)
        elif isinstance(data, list) and not isinstance(exposed_type, str):
            return pd.DataFrame.from_records([self._encoder(row) for row in data])
        return pd.DataFrame(data)

    @classmethod
    def _get_valid_exposed_type(cls, properties: Dict):
        if (
            cls._EXPOSED_TYPE_PROPERTY not in properties.keys()
            or properties[cls._EXPOSED_TYPE_PROPERTY] == cls._EXPOSED_TYPE_MODIN
        ):
            # Default exposed type is pandas
            # Deprecated modin exposed type in favor of pandas since 3.1.0
            return cls._EXPOSED_TYPE_PANDAS
        return properties[cls._EXPOSED_TYPE_PROPERTY]

    @classmethod
    def _check_exposed_type(cls, exposed_type):
        valid_string_exposed_types = cls._VALID_STRING_EXPOSED_TYPES
        if isinstance(exposed_type, str) and exposed_type not in valid_string_exposed_types:
            raise InvalidExposedType(
                f"Invalid string exposed type {exposed_type}. Supported values are "
                f"{', '.join(valid_string_exposed_types)}"
            )

    def _default_decoder_with_header(self, document: Dict) -> Any:
        if self.custom_document:
            return self.custom_document(**document)

    def _default_decoder_without_header(self, document: List) -> Any:
        if self.custom_document:
            return self.custom_document(*document)

    def _default_encoder(self, document_object: Any) -> Dict:
        return document_object.__dict__
