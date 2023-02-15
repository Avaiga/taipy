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

import os
from unittest import mock

from src.taipy.core.config import DataNodeConfig, PipelineConfig, ScenarioConfig, TaskConfig
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_write_configuration_file():
    expected_config = """
[TAIPY]
root_folder = "./taipy/"
storage_folder = ".data/"
clean_entities_enabled = "True:bool"
repository_type = "filesystem"

[JOB]
mode = "standalone"
max_nb_of_workers = "2:int"

[DATA_NODE.default]
storage_type = "in_memory"
custom = "default_custom_prop"

[DATA_NODE.dn1]
storage_type = "pickle"
scope = "PIPELINE:SCOPE"
custom = "custom property"
default_data = "dn1"

[DATA_NODE.dn2]
storage_type = "ENV[FOO]"
scope = "SCENARIO:SCOPE"
foo = "bar"
default_data = "dn2"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[TASK.default]
inputs = []
outputs = []
skippable = "False:bool"

[TASK.t1]
inputs = [ "dn1:SECTION",]
function = "builtins.print:function"
outputs = [ "dn2:SECTION",]
skippable = "False:bool"
description = "t1 description"

[PIPELINE.default]
tasks = []

[PIPELINE.p1]
tasks = [ "t1:SECTION",]
cron = "daily"

[SCENARIO.default]
pipelines = []
frequency = "QUARTERLY:FREQUENCY"
owner = "Michel Platini"

[SCENARIO.s1]
pipelines = [ "p1:SECTION",]
frequency = "QUARTERLY:FREQUENCY"
owner = "Raymond Kopa"

[SCENARIO.default.comparators]

[SCENARIO.s1.comparators]
    """.strip()
    tf = NamedTemporaryFile()
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.configure_global_app(clean_entities_enabled=True)
        Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
        Config.configure_default_data_node(storage_type="in_memory", custom="default_custom_prop")
        dn1_cfg_v2 = Config.configure_data_node(
            "dn1", storage_type="pickle", scope=Scope.PIPELINE, default_data="dn1", custom="custom property"
        )
        dn2_cfg_v2 = Config.configure_data_node(
            "dn2",
            storage_type="ENV[FOO]",
            foo="bar",
            default_data="dn2",
            baz="ENV[QUX]",
            quux="ENV[QUUZ]:bool",
            corge=("grault", "ENV[GARPLY]", "ENV[WALDO]:int", 3.0),
        )
        assert dn2_cfg_v2.scope == Scope.SCENARIO
        t1_cfg_v2 = Config.configure_task("t1", print, dn1_cfg_v2, dn2_cfg_v2, description="t1 description")
        p1_cfg_v2 = Config.configure_pipeline("p1", t1_cfg_v2, cron="daily")
        Config.configure_default_scenario([], Frequency.QUARTERLY, owner="Michel Platini")
        Config.configure_scenario("s1", p1_cfg_v2, frequency=Frequency.QUARTERLY, owner="Raymond Kopa")
        Config.backup(tf.filename)
        actual_config = tf.read().strip()

        assert actual_config == expected_config
        Config.load(tf.filename)
        tf2 = NamedTemporaryFile()
        Config.backup(tf2.filename)
        actual_config_2 = tf2.read().strip()
        assert actual_config_2 == expected_config


def test_read_configuration_file():
    file_config = NamedTemporaryFile(
        """
        [DATA_NODE.default]
        has_header = true

        [DATA_NODE.my_datanode]
        path = "/data/csv"

        [DATA_NODE.my_datanode2]
        path = "/data2/csv"

        [TASK.my_task]
        inputs = ["my_datanode:SECTION"]
        outputs = ["my_datanode2:SECTION"]
        description = "task description"

        [PIPELINE.my_pipeline]
        tasks = [ "my_task:SECTION",]
        cron = "daily"

        [SCENARIO.my_scenario]
        pipelines = [ "my_pipeline:SECTION",]
        owner = "John Doe"
        """
    )
    Config.configure_task("my_task", print)
    Config.load(file_config.filename)

    assert len(Config.data_nodes) == 3
    assert type(Config.data_nodes["my_datanode"]) == DataNodeConfig
    assert type(Config.data_nodes["my_datanode2"]) == DataNodeConfig
    assert Config.data_nodes["my_datanode"].path == "/data/csv"
    assert Config.data_nodes["my_datanode2"].path == "/data2/csv"
    assert Config.data_nodes["my_datanode"].id == "my_datanode"
    assert Config.data_nodes["my_datanode2"].id == "my_datanode2"

    assert len(Config.tasks) == 2
    assert type(Config.tasks["my_task"]) == TaskConfig
    assert Config.tasks["my_task"].id == "my_task"
    assert Config.tasks["my_task"].description == "task description"
    assert Config.tasks["my_task"].function == print
    assert len(Config.tasks["my_task"].inputs) == 1
    assert type(Config.tasks["my_task"].inputs[0]) == DataNodeConfig
    assert Config.tasks["my_task"].inputs[0].path == "/data/csv"
    assert Config.tasks["my_task"].inputs[0].id == "my_datanode"
    assert len(Config.tasks["my_task"].outputs) == 1
    assert type(Config.tasks["my_task"].outputs[0]) == DataNodeConfig
    assert Config.tasks["my_task"].outputs[0].path == "/data2/csv"
    assert Config.tasks["my_task"].outputs[0].id == "my_datanode2"

    assert len(Config.pipelines) == 2
    assert type(Config.pipelines["my_pipeline"]) == PipelineConfig
    assert Config.pipelines["my_pipeline"].id == "my_pipeline"
    assert Config.pipelines["my_pipeline"].cron == "daily"
    assert len(Config.pipelines["my_pipeline"].tasks) == 1
    assert type(Config.pipelines["my_pipeline"].tasks[0]) == TaskConfig
    assert Config.pipelines["my_pipeline"].tasks[0].id == "my_task"
    assert Config.pipelines["my_pipeline"].tasks[0].description == "task description"

    assert len(Config.scenarios) == 2
    assert type(Config.scenarios["my_scenario"]) == ScenarioConfig
    assert Config.scenarios["my_scenario"].id == "my_scenario"
    assert Config.scenarios["my_scenario"].owner == "John Doe"
    assert len(Config.scenarios["my_scenario"].pipelines) == 1
    assert type(Config.scenarios["my_scenario"].pipelines[0]) == PipelineConfig
    assert Config.scenarios["my_scenario"].pipelines[0].id == "my_pipeline"
    assert Config.scenarios["my_scenario"].pipelines[0].cron == "daily"
