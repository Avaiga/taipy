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

import json

from taipy.core._entity._migrate._utils import _migrate


# @pytest.mark.parametrize("migrate_fct,data")
def test_migrate_entities_before_version_3():
    with open("tests/core/_entity/data_to_migrate.json") as file:
        data = json.load(file)

    with open("tests/core/_entity/expected_data.json") as file:
        expected_data = json.load(file)

    migrated_data, _ = _migrate(data)

    assert expected_data == migrated_data

    # Execute again on the migrated data to ensure that the migration  works on latest versions
    migrated_data, _ = _migrate(data)
    assert expected_data == migrated_data
