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

from typing import List, Optional, Union

from .._entity._entity import _Entity
from .._entity._reload import _get_manager
from .._manager._manager import _Manager


def _check_entity_and_get_manager(entity: Union[_Entity, str], possible_classes: List) -> Optional[_Manager]:
    for possible_class in possible_classes:
        if isinstance(entity, possible_class) or (
            isinstance(entity, str) and entity.startswith(possible_class._ID_PREFIX)  # type: ignore
        ):
            return _get_manager(possible_class._MANAGER_NAME)  # type: ignore
    return None
