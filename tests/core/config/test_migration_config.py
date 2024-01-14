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

from taipy.config.config import Config


def migrate_pickle_path(dn):
    dn.path = "s1.pkl"


def migrate_skippable(task):
    task.skippable = True


def test_migration_config():
    assert Config.migration_functions.migration_fcts == {}

    data_nodes1 = Config.configure_data_node("data_nodes1", "pickle")

    migration_cfg = Config.add_migration_function(
        target_version="1.0",
        config=data_nodes1,
        migration_fct=migrate_pickle_path,
    )

    assert migration_cfg.migration_fcts == {"1.0": {"data_nodes1": migrate_pickle_path}}
    assert migration_cfg.properties == {}

    data_nodes2 = Config.configure_data_node("data_nodes2", "pickle")

    migration_cfg = Config.add_migration_function(
        target_version="1.0",
        config=data_nodes2,
        migration_fct=migrate_pickle_path,
    )
    assert migration_cfg.migration_fcts == {
        "1.0": {"data_nodes1": migrate_pickle_path, "data_nodes2": migrate_pickle_path}
    }


def test_clean_config():
    assert Config.migration_functions.migration_fcts == {}

    data_nodes1 = Config.configure_data_node("data_nodes1", "pickle")
    migration_cfg = Config.add_migration_function(
        target_version="1.0",
        config=data_nodes1,
        migration_fct=migrate_pickle_path,
    )

    assert migration_cfg.migration_fcts == {"1.0": {"data_nodes1": migrate_pickle_path}}
    assert migration_cfg.properties == {}

    migration_cfg._clean()

    assert migration_cfg.migration_fcts == {}
    assert migration_cfg._properties == {}
