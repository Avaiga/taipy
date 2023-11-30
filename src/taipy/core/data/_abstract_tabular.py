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

from ..exceptions.exceptions import InvalidExposedType


class _AbstractTabularDataNode(object):
    """Abstract base class for tabular data node implementations (CSVDataNode, ParquetDataNode, ExcelDataNode,
    SQLTableDataNode and SQLDataNode) that are tabular representable."""

    @staticmethod
    def _check_exposed_type(exposed_type, valid_string_exposed_types):
        if isinstance(exposed_type, str) and exposed_type not in valid_string_exposed_types:
            raise InvalidExposedType(
                f"Invalid string exposed type {exposed_type}. Supported values are "
                f"{', '.join(valid_string_exposed_types)}"
            )
