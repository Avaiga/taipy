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

from datetime import datetime

from src.taipy.core.scenario._scenario_fs_repository_v2 import _ScenarioFSRepository
from src.taipy.core.scenario.scenario import Scenario


def test_save_and_load(tmpdir, scenario):
    repository = _ScenarioFSRepository()
    repository.base_path = tmpdir
    repository._save(scenario)
    cc = repository._load(scenario.id)

    assert isinstance(cc, Scenario)
    assert cc.id == scenario.id
    assert cc.name == scenario.name
    assert cc.creation_date == scenario.creation_date
