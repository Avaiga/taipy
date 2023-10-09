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

import pytest

from src.taipy.core._migrate import _migrate_entity


@pytest.mark.parametrize(
    "entity",
    [
        "SCENARIO",
        "TASK",
        "DATANODE",
        "JOB",
        "VERSION",
    ],
)
def test_migrate_entity(entity, entities_for_migration, expected_entities_for_migration):
    migrated_data = _migrate_entity(entity, entities_for_migration)
    entities = {k: migrated_data[k] for k in migrated_data if entity in k}
    expected_entities = {k: expected_entities_for_migration[k] for k in expected_entities_for_migration if entity in k}

    assert entities == expected_entities
