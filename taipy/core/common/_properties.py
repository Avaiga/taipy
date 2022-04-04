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

from collections import UserDict


class _Properties(UserDict):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def __setitem__(self, key, value):
        super(_Properties, self).__setitem__(key, value)
        import taipy.core.taipy as tp

        if hasattr(self, "parent"):
            tp.set(self.parent)
