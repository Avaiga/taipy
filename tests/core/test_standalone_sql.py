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

import logging
import os

import pytest

from taipy.config.config import Config
from taipy.core import Core
from taipy.core.scenario._scenario_manager import _ScenarioManager
from tests.core.utils import assert_true_after_time


def configure():
    data_node_1_config = Config.configure_data_node(id="d1", storage_type="pickle", default_data="abc")
    data_node_2_config = Config.configure_data_node(
        id="d2",
        storage_type="pickle",
    )
    task_config = Config.configure_task("my_task", display, data_node_1_config, data_node_2_config)
    scenario_config = Config.configure_scenario("my_scenario", [task_config])

    return scenario_config


def display(data):
    logging.info(data)
    return data


@pytest.fixture(scope="function")
def tmp_sqlite(tmpdir_factory):
    fn = tmpdir_factory.mktemp("db")
    return os.path.join(fn.strpath, "test.db")


def test_standalone_sql(tmp_sqlite):
    scenario_config = configure()
    Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
    core = Core()
    core.run(force_restart=True)
    scenario = _ScenarioManager._create(scenario_config)

    jobs = _ScenarioManager._submit(scenario).jobs
    assert_true_after_time(lambda: all(job.is_finished() for job in jobs), time=2)
    core.stop()
    assert_true_after_time(lambda: core._dispatcher is None, time=2)
