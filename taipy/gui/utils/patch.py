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

import typing as t

from . import _MapDict


def _patch_value(value: t.Any, change: t.Optional[dict] = None, remove: t.Optional[dict] = None) -> t.Any:  # noqa: C901
    original_value = value
    if isinstance(value, _MapDict):
        value = value._dict
    # TODO handle dataframe
    if isinstance(value, dict):
        if change:
            for k, v in change.items():
                if k in value:
                    if isinstance(v, dict):
                        value[k] = _patch_value(value[k], v)
                    else:
                        value[k] = v
        if remove:
            for k, v in remove.items():
                if k in value:
                    if isinstance(v, dict):
                        value[k] = _patch_value(value[k], remove=v)
                    else:
                        del value[k]
    elif isinstance(value, list):
        if change:
            for k, v in change.items():
                if isinstance(k, int) and 0 <= k < len(value):
                    if isinstance(v, dict):
                        value[k] = _patch_value(value[k], v)
                    else:
                        if isinstance(v, list):
                            for idx, nv in enumerate(v, start=k):
                                if idx < len(value):
                                    value[idx] = (
                                        _patch_value(value[idx], nv)
                                        if isinstance(nv, dict)
                                        else nv
                                    )
                                else:
                                    value.append(nv)
                        else:
                            value[k] = v
        if remove:
            # To avoid index shift, we sort the keys in reverse order
            for k in sorted(remove.keys(), reverse=True):
                if isinstance(k, int) and 0 <= k < len(value):
                    v = remove[k]
                    if isinstance(v, dict):
                        value[k] = _patch_value(value[k], remove=v)
                    else:
                        del value[k]
    return original_value
