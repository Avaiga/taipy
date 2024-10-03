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

from taipy.common.logger._taipy_logger import _TaipyLogger

from .utils.singleton import _Singleton


class _Hook:
    method_names: t.List[str] = []


class _Hooks(object, metaclass=_Singleton):
    def __init__(self):
        self.__hooks: t.List[_Hook] = []  # type: ignore[annotation-unchecked]

    def _register_hook(self, hook: _Hook):
        # Prevent duplicated hooks
        for h in self.__hooks:
            if type(hook) is type(h):
                _TaipyLogger._get_logger().info(f"Failed to register duplicated hook of type '{type(h)}'")
                return
        self.__hooks.append(hook)

    def __getattr__(self, name: str):
        def _resolve_hook(*args, **kwargs):
            for hook in self.__hooks:
                if name not in hook.method_names:
                    continue
                # call hook
                try:
                    func = getattr(hook, name)
                    if not callable(func):
                        raise Exception(f"'{name}' hook is not callable")
                    res = getattr(hook, name)(*args, **kwargs)
                except Exception as e:
                    _TaipyLogger._get_logger().error(f"Error while calling hook '{name}': {e}")
                    return
                # check if the hook returns True -> stop the chain
                if res is True:
                    return
                # only hooks that return true are allowed to return values to ensure consistent response
                if isinstance(res, (list, tuple)) and len(res) == 2 and res[0] is True:
                    return res[1]

        return _resolve_hook
