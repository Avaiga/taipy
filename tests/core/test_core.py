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


import pytest

from taipy.core import Core, Orchestrator


class TestCore:
    def test_run_core_with_depracated_message(self, caplog):
        with pytest.warns(DeprecationWarning):
            core = Core()
        core.run()

        assert isinstance(core, Orchestrator)
        expected_message = (
            "The `Core` service is deprecated and replaced by the `Orchestrator` service. "
            "An `Orchestrator` instance has been instantiated instead."
        )
        assert expected_message in caplog.text

        core.stop()
