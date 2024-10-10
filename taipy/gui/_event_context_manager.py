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
from threading import Thread


class _EventManager:
    def __init__(self) -> None:
        self.__thread_stack: t.List[Thread] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__thread_stack:
            self.__thread_stack.pop().start()
        return self

    def _add_thread(self, thread: Thread):
        self.__thread_stack.append(thread)
