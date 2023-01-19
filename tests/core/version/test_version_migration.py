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
import json
import os
import pathlib
import shutil
from unittest.mock import patch

from src.taipy.core import Core, taipy
from src.taipy.core._repository import _CustomDecoder
from src.taipy.core._version._version_manager import _VersionManager
from taipy import Config, Frequency


def test_experiment_mode_converts_old_entities_to_latest_version():
    version = "1.0"
    with patch("sys.argv", ["prog", "--experiment", version]):
        file_names = init_migration_test()

        Core().run()
        scenario = taipy.get("SCENARIO_my_scenario_c4307ae8-d2ce-4802-8b16-8307baa7cff1")
        assert _VersionManager._get_development_version() != version
        assert version not in _VersionManager._get_production_version()
        assert scenario.version == version
        assert scenario.my_pipeline.version == version
        assert scenario.my_pipeline.my_task.version == version
        assert scenario.d1.version == version
        assert scenario.d2.version == version
        assert_data_migrated(file_names, version)


def test_production_mode_converts_old_entities_to_latest_version():
    version = "1.0"
    with patch("sys.argv", ["prog", "--production", version]):
        file_names = init_migration_test()

        Core().run()
        scenario = taipy.get("SCENARIO_my_scenario_c4307ae8-d2ce-4802-8b16-8307baa7cff1")
        assert _VersionManager._get_development_version() != version
        assert version in _VersionManager._get_production_version()
        assert scenario.version == version
        assert scenario.my_pipeline.version == version
        assert scenario.my_pipeline.my_task.version == version
        assert scenario.d1.version == version
        assert scenario.d2.version == version
        assert_data_migrated(file_names, version)


def test_development_mode_converts_old_entities_to_latest_version():
    with patch("sys.argv", ["prog", "--development", "1.0"]):
        file_names = init_migration_test()

        Core().run()
        scenario = taipy.get("SCENARIO_my_scenario_c4307ae8-d2ce-4802-8b16-8307baa7cff1")
        version = "LEGACY-VERSION"
        assert _VersionManager._get_development_version() != version
        assert version not in _VersionManager._get_production_version()
        assert scenario.version == version
        assert scenario.my_pipeline.version == version
        assert scenario.my_pipeline.my_task.version == version
        assert scenario.d1.version == version
        assert scenario.d2.version == version

        assert_data_migrated(file_names, version)


def init_migration_test():
    config_scenario()
    shutil.rmtree(Config.global_config.storage_folder, ignore_errors=True)
    data_set_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset_2.0/")
    shutil.copytree(data_set_path, Config.global_config.storage_folder)
    file_names = [
        ("scenarios", "SCENARIO_my_scenario_c4307ae8-d2ce-4802-8b16-8307baa7cff1.json"),
        ("pipelines", "PIPELINE_my_pipeline_1b97a539-ca51-4eb8-aa64-c232269618c6.json"),
        ("tasks", "TASK_my_task_53cf9993-047f-4220-9c03-e28fa250f6b3.json"),
        ("data_nodes", "DATANODE_d1_3d65c33b-b188-4402-8d2c-3b26d98b9a9e.json"),
        ("data_nodes", "DATANODE_d2_bd8ee43e-6fa9-4832-b2e7-c0c9516b1e1c.json"),
    ]
    assert_data_migrated(file_names, None)
    return file_names


def assert_data_migrated(file_names, version):
    for file in file_names:
        path = os.path.join(Config.global_config.storage_folder, *file)
        with open(path, "r") as f:
            file_content = f.read()
            data = json.loads(file_content, cls=_CustomDecoder)
            assert data.get("version") == version


def twice(a):
    return a * 2


def config_scenario():
    data_node_1_config = Config.configure_data_node(id="d1", storage_type="in_memory", default_data="abc")
    data_node_2_config = Config.configure_data_node(id="d2", storage_type="csv", default_path="foo.csv")
    task_config = Config.configure_task("my_task", twice, data_node_1_config, data_node_2_config)
    pipeline_config = Config.configure_pipeline("my_pipeline", task_config)
    scenario_config = Config.configure_scenario("my_scenario", pipeline_config, frequency=Frequency.DAILY)
    return scenario_config
