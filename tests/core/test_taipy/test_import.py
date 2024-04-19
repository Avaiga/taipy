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

import os
import shutil

import pandas as pd
import pytest

import taipy.core.taipy as tp
from taipy import Config, Frequency, Scope
from taipy.core._version._version_manager import _VersionManager
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.exceptions.exceptions import (
    ConflictedConfigurationError,
    ImportFolderDoesntContainAnyScenario,
    ImportScenarioDoesntHaveAVersion,
)
from taipy.core.job._job_manager import _JobManager
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.submission._submission_manager import _SubmissionManager
from taipy.core.task._task_manager import _TaskManager


@pytest.fixture(scope="function", autouse=True)
def clean_tmp_folder():
    shutil.rmtree("./tmp", ignore_errors=True)
    yield
    shutil.rmtree("./tmp", ignore_errors=True)


def plus_1(x):
    return x + 1


def plus_1_dataframe(x):
    return pd.DataFrame({"output": [x + 1]})


def configure_test_scenario(input_data, frequency=None):
    input_cfg = Config.configure_data_node(
        id=f"i_{input_data}", storage_type="pickle", scope=Scope.SCENARIO, default_data=input_data
    )
    csv_output_cfg = Config.configure_data_node(id=f"o_{input_data}_csv", storage_type="csv")
    excel_output_cfg = Config.configure_data_node(id=f"o_{input_data}_excel", storage_type="excel")
    parquet_output_cfg = Config.configure_data_node(id=f"o_{input_data}_parquet", storage_type="parquet")
    json_output_cfg = Config.configure_data_node(id=f"o_{input_data}_json", storage_type="json")

    csv_task_cfg = Config.configure_task(f"t_{input_data}_csv", plus_1_dataframe, input_cfg, csv_output_cfg)
    excel_task_cfg = Config.configure_task(f"t_{input_data}_excel", plus_1_dataframe, input_cfg, excel_output_cfg)
    parquet_task_cfg = Config.configure_task(f"t_{input_data}_parquet", plus_1_dataframe, input_cfg, parquet_output_cfg)
    json_task_cfg = Config.configure_task(f"t_{input_data}_json", plus_1, input_cfg, json_output_cfg)
    scenario_cfg = Config.configure_scenario(
        id=f"s_{input_data}",
        task_configs=[csv_task_cfg, excel_task_cfg, parquet_task_cfg, json_task_cfg],
        frequency=frequency,
    )

    return scenario_cfg


def export_test_scenario(scenario_cfg, folder_path="./tmp/exp_scenario", override=False, include_data=False):
    scenario = tp.create_scenario(scenario_cfg)
    tp.submit(scenario)

    # Export the submitted scenario
    tp.export_scenario(scenario.id, folder_path, override, include_data)
    return scenario


def test_import_scenario_without_data(init_managers):
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    scenario = export_test_scenario(scenario_cfg)

    init_managers()

    assert _ScenarioManager._get_all() == []
    imported_scenario = tp.import_scenario("./tmp/exp_scenario")

    # The imported scenario should be the same as the exported scenario
    assert _ScenarioManager._get_all() == [imported_scenario]
    assert imported_scenario == scenario

    # All entities belonging to the scenario should be imported
    assert len(_CycleManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 4
    assert len(_DataManager._get_all()) == 5
    assert len(_JobManager._get_all()) == 4
    assert len(_SubmissionManager._get_all()) == 1
    assert len(_VersionManager._get_all()) == 1


def test_import_scenario_with_data(init_managers):
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    export_test_scenario(scenario_cfg, include_data=True)

    init_managers()

    assert _ScenarioManager._get_all() == []
    imported_scenario = tp.import_scenario("./tmp/exp_scenario")

    # All data of all data nodes should be imported
    assert all(os.path.exists(dn.path) for dn in imported_scenario.data_nodes.values())


def test_import_scenario_when_entities_are_already_existed_should_rollback(caplog):
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    export_test_scenario(scenario_cfg)

    caplog.clear()

    _CycleManager._delete_all()
    _TaskManager._delete_all()
    _DataManager._delete_all()
    _JobManager._delete_all()
    _ScenarioManager._delete_all()

    assert len(_CycleManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0
    assert len(_SubmissionManager._get_all()) == 1  # Keep the submission entity to test the rollback
    submission_id = _SubmissionManager._get_all()[0].id
    assert len(_ScenarioManager._get_all()) == 0

    # Import the scenario when the old entities still exist
    imported_entity = tp.import_scenario("./tmp/exp_scenario")
    assert imported_entity is None
    assert all(log.levelname in ["ERROR", "INFO"] for log in caplog.records)
    assert "An error occurred during the import" in caplog.text
    assert f"{submission_id} already exists. Please use the 'override' parameter to override it" in caplog.text

    # No entity should be imported and the old entities should be kept
    assert len(_CycleManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0
    assert len(_SubmissionManager._get_all()) == 1  # Keep the submission entity to test the rollback
    assert len(_ScenarioManager._get_all()) == 0

    caplog.clear()

    # Import with override flag
    tp.import_scenario("./tmp/exp_scenario", override=True)
    assert all(log.levelname in ["WARNING", "INFO"] for log in caplog.records)
    assert f"{submission_id} already exists and will be overridden" in caplog.text

    # The scenario is imported and overridden the old one
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 4
    assert len(_DataManager._get_all()) == 5
    assert len(_JobManager._get_all()) == 4
    assert len(_SubmissionManager._get_all()) == 1
    assert len(_VersionManager._get_all()) == 1


def test_import_incompatible_scenario(init_managers):
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    export_test_scenario(scenario_cfg)

    Config.unblock_update()

    # Configure a new dn to make the exported version incompatible
    Config.configure_data_node("new_dn")

    with pytest.raises(ConflictedConfigurationError):
        tp.import_scenario("./tmp/exp_scenario")


def test_import_a_non_exists_folder():
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    export_test_scenario(scenario_cfg)

    with pytest.raises(FileNotFoundError):
        tp.import_scenario("non_exists_folder")


def test_import_an_empty_folder(tmpdir_factory):
    empty_folder = tmpdir_factory.mktemp("empty_folder").strpath

    with pytest.raises(ImportFolderDoesntContainAnyScenario):
        tp.import_scenario(empty_folder)


def test_import_with_no_version():
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    export_test_scenario(scenario_cfg)
    shutil.rmtree("./tmp/exp_scenario/version")

    with pytest.raises(ImportScenarioDoesntHaveAVersion):
        tp.import_scenario("./tmp/exp_scenario")
