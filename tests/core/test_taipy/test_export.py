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
from taipy.core.exceptions import ExportFolderAlreadyExists, InvalidExportPath


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


def test_export_scenario_to_the_storage_folder():
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    scenario = tp.create_scenario(scenario_cfg)

    with pytest.raises(InvalidExportPath):
        tp.export_scenario(scenario.id, Config.core.taipy_storage_folder)


def test_export_scenario_with_cycle():
    scenario_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)

    scenario = tp.create_scenario(scenario_cfg)
    jobs = tp.submit(scenario).jobs

    # Export the submitted scenario
    tp.export_scenario(scenario.id, "./tmp/exp_scenario")

    assert sorted(os.listdir("./tmp/exp_scenario/data_nodes")) == sorted(
        [
            f"{scenario.i_1.id}.json",
            f"{scenario.o_1_csv.id}.json",
            f"{scenario.o_1_excel.id}.json",
            f"{scenario.o_1_parquet.id}.json",
            f"{scenario.o_1_json.id}.json",
        ]
    )
    assert sorted(os.listdir("./tmp/exp_scenario/tasks")) == sorted(
        [
            f"{scenario.t_1_csv.id}.json",
            f"{scenario.t_1_excel.id}.json",
            f"{scenario.t_1_parquet.id}.json",
            f"{scenario.t_1_json.id}.json",
        ]
    )
    assert sorted(os.listdir("./tmp/exp_scenario/scenarios")) == sorted([f"{scenario.id}.json"])
    assert sorted(os.listdir("./tmp/exp_scenario/jobs")) == sorted(
        [f"{jobs[0].id}.json", f"{jobs[1].id}.json", f"{jobs[2].id}.json", f"{jobs[3].id}.json"]
    )
    assert sorted(os.listdir("./tmp/exp_scenario/cycles")) == sorted([f"{scenario.cycle.id}.json"])


def test_export_scenario_without_cycle():
    scenario_cfg = configure_test_scenario(1)

    scenario = tp.create_scenario(scenario_cfg)
    tp.submit(scenario)

    # Export the submitted scenario
    tp.export_scenario(scenario.id, "./tmp/exp_scenario")

    assert os.path.exists("./tmp/exp_scenario/data_nodes")
    assert os.path.exists("./tmp/exp_scenario/tasks")
    assert os.path.exists("./tmp/exp_scenario/scenarios")
    assert os.path.exists("./tmp/exp_scenario/jobs")
    assert not os.path.exists("./tmp/exp_scenario/cycles")  # No cycle


def test_export_scenario_override_existing_files():
    scenario_1_cfg = configure_test_scenario(1, frequency=Frequency.DAILY)
    scenario_2_cfg = configure_test_scenario(2)

    scenario_1 = tp.create_scenario(scenario_1_cfg)
    tp.submit(scenario_1)

    # Export the submitted scenario_1
    tp.export_scenario(scenario_1.id, "./tmp/exp_scenario")
    assert os.path.exists("./tmp/exp_scenario/data_nodes")
    assert os.path.exists("./tmp/exp_scenario/tasks")
    assert os.path.exists("./tmp/exp_scenario/scenarios")
    assert os.path.exists("./tmp/exp_scenario/jobs")
    assert os.path.exists("./tmp/exp_scenario/cycles")

    scenario_2 = tp.create_scenario(scenario_2_cfg)
    tp.submit(scenario_2)

    # Export the submitted scenario_2 to the same folder should raise an error
    with pytest.raises(ExportFolderAlreadyExists):
        tp.export_scenario(scenario_2.id, "./tmp/exp_scenario")

    # Export the submitted scenario_2 without a cycle and override the existing files
    tp.export_scenario(scenario_2.id, "./tmp/exp_scenario", override=True)
    assert os.path.exists("./tmp/exp_scenario/data_nodes")
    assert os.path.exists("./tmp/exp_scenario/tasks")
    assert os.path.exists("./tmp/exp_scenario/scenarios")
    assert os.path.exists("./tmp/exp_scenario/jobs")
    # The cycles folder should be removed when overriding
    assert not os.path.exists("./tmp/exp_scenario/cycles")


def test_export_scenario_filesystem_with_data():
    scenario_cfg = configure_test_scenario(1)
    scenario = tp.create_scenario(scenario_cfg)
    tp.submit(scenario)

    # Export scenario without data
    tp.export_scenario(scenario.id, "./tmp/exp_scenario")
    assert not os.path.exists("./tmp/exp_scenario/user_data")

    # Export scenario with data
    tp.export_scenario(scenario.id, "./tmp/exp_scenario", include_data=True, override=True)
    assert os.path.exists("./tmp/exp_scenario/user_data")
    assert sorted(os.listdir("./tmp/exp_scenario/user_data")) == sorted(
        [
            f"{scenario.i_1.id}.p",
            f"{scenario.o_1_csv.id}.csv",
            f"{scenario.o_1_excel.id}.xlsx",
            f"{scenario.o_1_parquet.id}.parquet",
            f"{scenario.o_1_json.id}.json",
        ]
    )


def test_export_non_file_based_data_node_raise_warning(caplog):
    input_cfg = Config.configure_data_node(id="i", storage_type="pickle", scope=Scope.SCENARIO, default_data=1)
    csv_output_cfg = Config.configure_data_node(id="o_csv", storage_type="csv")
    in_mem_output_cfg = Config.configure_data_node(id="o_mem", storage_type="in_memory")

    csv_task_cfg = Config.configure_task("t_csv", plus_1_dataframe, input_cfg, csv_output_cfg)
    in_mem_task_cfg = Config.configure_task("t_mem", plus_1, input_cfg, in_mem_output_cfg)
    scenario_cfg = Config.configure_scenario(id="s", task_configs=[csv_task_cfg, in_mem_task_cfg])

    scenario = tp.create_scenario(scenario_cfg)
    tp.submit(scenario)

    # Export scenario with in-memory data node
    tp.export_scenario(scenario.id, "./tmp/exp_scenario", include_data=True)
    expected_warning = f"Data node {scenario.o_mem.id} is not a file-based data node and the data will not be exported"
    assert expected_warning in caplog.text
