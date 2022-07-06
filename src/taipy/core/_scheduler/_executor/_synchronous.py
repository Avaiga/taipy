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

from concurrent.futures import Executor, Future


class _Synchronous(Executor):
    """
    Similar to the Python standard Thread/Process Pool Executor but the function is executed directly in a
    synchronous mode.
    """

    @staticmethod
    def submit(fn, /, *args, **kwargs):
        """Execute the function submitted in a synchronous mode."""
        future: Future = Future()

        try:
            future.set_result(fn(*args, **kwargs))
        except Exception as e:
            future.set_exception(e)

        return future
