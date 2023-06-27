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
import abc
from typing import Optional


class _Labeled:
    __LABEL_SEPARATOR = " > "

    @abc.abstractmethod
    def get_label(self) -> str:
        raise NotImplementedError

    def _get_label(self) -> str:
        """Returns the entity label made of the simple label prefixed by the owner label.

        Returns:
            The label of the entity as a string.
        """
        return self._get_explicit_label() or self._generate_label()

    @abc.abstractmethod
    def get_simple_label(self) -> str:
        raise NotImplementedError

    def _get_simple_label(self) -> str:
        """Returns the simple label.

        Returns:
            The simple label of the entity as a string.
        """
        return self._get_explicit_label() or self._generate_label(True)

    def _generate_label(self, simple=False) -> str:
        ls = []
        if not simple:
            if owner_id := self._get_owner_id():
                if getattr(self, "id") != owner_id:
                    from ... import core as tp

                    owner = tp.get(owner_id)
                    ls.append(owner.get_label())
        ls.append(self._generate_entity_label())
        return self.__LABEL_SEPARATOR.join(ls)

    def _get_explicit_label(self) -> Optional[str]:
        if hasattr(self, "_properties"):
            return getattr(self, "_properties").get("label")
        return None

    def _get_owner_id(self) -> Optional[str]:
        if hasattr(self, "owner_id"):
            return getattr(self, "owner_id")
        return None

    def _get_name(self) -> Optional[str]:
        if hasattr(self, "name"):
            return getattr(self, "name")
        if hasattr(self, "_properties"):
            return getattr(self, "_properties").get("name")
        return None

    def _get_config_id(self) -> Optional[str]:
        if hasattr(self, "config_id"):
            return getattr(self, "config_id")
        return None

    def _generate_entity_label(self) -> str:
        if name := self._get_name():
            return name
        if config_id := self._get_config_id():
            return config_id
        return getattr(self, "id")
