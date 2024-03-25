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


def _is_boolean_true(s: t.Union[bool, str]) -> bool:
    return (
        s
        if isinstance(s, bool)
        else s.lower() in ["true", "1", "t", "y", "yes", "yeah", "sure"] if isinstance(s, str) else False
    )


def _is_boolean(s: t.Any) -> bool:
    if isinstance(s, bool):
        return True
    elif isinstance(s, str):
        return s.lower() in ["true", "1", "t", "y", "yes", "yeah", "sure", "false", "0", "f", "no"]
    else:
        return False
