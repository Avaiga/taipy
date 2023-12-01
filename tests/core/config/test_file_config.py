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
from datetime import timedelta
from unittest import mock

from src.taipy.config.common.frequency import Frequency
from src.taipy.config.common.scope import Scope
from src.taipy.config.config import Config
from src.taipy.core.config import DataNodeConfig, ScenarioConfig, TaskConfig
from src.taipy.core.config.core_section import CoreSection
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_write_configuration_file():
    expected_config = f"""
[TAIPY]

[JOB]
mode = "standalone"
max_nb_of_workers = "2:int"

[CORE]
root_folder = "./taipy/"
storage_folder = ".data/"
repository_type = "filesystem"
read_entity_retry = "0:int"
mode = "development"
version_number = ""
force = "False:bool"
core_version = "{CoreSection._CURRENT_CORE_VERSION}"

[VERSION_MIGRATION.migration_fcts]

[DATA_NODE.default]
storage_type = "in_memory"
scope = "SCENARIO:SCOPE"
validity_period = "1d0h0m0s:timedelta"
custom = "default_custom_prop"

[DATA_NODE.dn1]
storage_type = "pickle"
scope = "SCENARIO:SCOPE"
validity_period = "1d0h0m0s:timedelta"
custom = "custom property"
default_data = "dn1"

[DATA_NODE.dn2]
storage_type = "ENV[FOO]"
scope = "SCENARIO:SCOPE"
validity_period = "2d0h0m0s:timedelta"
foo = "bar"
default_data = "dn2"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[DATA_NODE.dn3]
storage_type = "ENV[FOO]"
scope = "SCENARIO:SCOPE"
validity_period = "1d0h0m0s:timedelta"
foo = "bar"
default_data = "dn3"
quux = "ENV[QUUZ]:bool"

[TASK.default]
inputs = []
outputs = []
skippable = "False:bool"

[TASK.t1]
function = "builtins.print:function"
inputs = [ "dn1:SECTION",]
outputs = [ "dn2:SECTION",]
skippable = "False:bool"
description = "t1 description"

[SCENARIO.default]
tasks = []
additional_data_nodes = []
frequency = "QUARTERLY:FREQUENCY"
owner = "Michel Platini"

[SCENARIO.s1]
tasks = [ "t1:SECTION",]
additional_data_nodes = [ "dn3:SECTION",]
frequency = "QUARTERLY:FREQUENCY"
owner = "Raymond Kopa"

[SCENARIO.default.comparators]

[SCENARIO.default.sequences]

[SCENARIO.s1.comparators]

[SCENARIO.s1.sequences]
sequence = [ "t1:SECTION",]
    """.strip()
    tf = NamedTemporaryFile()
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
        Config.set_default_data_node_configuration(
            storage_type="in_memory",
            custom="default_custom_prop",
            validity_period=timedelta(1),
        )
        dn1_cfg_v2 = Config.configure_data_node(
            "dn1", storage_type="pickle", scope=Scope.SCENARIO, default_data="dn1", custom="custom property"
        )
        dn2_cfg_v2 = Config.configure_data_node(
            "dn2",
            storage_type="ENV[FOO]",
            validity_period=timedelta(2),
            foo="bar",
            default_data="dn2",
            baz="ENV[QUX]",
            quux="ENV[QUUZ]:bool",
            corge=("grault", "ENV[GARPLY]", "ENV[WALDO]:int", 3.0),
        )
        dn3_cfg_v2 = Config.configure_data_node(
            "dn3",
            storage_type="ENV[FOO]",
            foo="bar",
            default_data="dn3",
            quux="ENV[QUUZ]:bool",
        )
        assert dn2_cfg_v2.scope == Scope.SCENARIO
        t1_cfg_v2 = Config.configure_task("t1", print, dn1_cfg_v2, dn2_cfg_v2, description="t1 description")
        Config.set_default_scenario_configuration([], [], Frequency.QUARTERLY, owner="Michel Platini")
        Config.configure_scenario(
            "s1",
            task_configs=[t1_cfg_v2],
            additional_data_node_configs=[dn3_cfg_v2],
            frequency=Frequency.QUARTERLY,
            owner="Raymond Kopa",
            sequences={"sequence": [t1_cfg_v2]},
        )
        Config.backup(tf.filename)
        actual_config = tf.read().strip()  # problem here

        assert actual_config == expected_config
        Config.override(tf.filename)
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
        validity_period = "1d0h0m0s:timedelta"

        [DATA_NODE.my_datanode2]
        path = "/data2/csv"

        [DATA_NODE.my_datanode3]
        path = "/data3/csv"
        source = "local"

        [TASK.my_task]
        inputs = ["my_datanode:SECTION"]
        outputs = ["my_datanode2:SECTION"]
        description = "task description"

        [SCENARIO.my_scenario]
        tasks = [ "my_task:SECTION"]
        additional_data_nodes = ["my_datanode3:SECTION"]
        owner = "John Doe"

        [SCENARIO.my_scenario.sequences]
        sequence = [ "my_task:SECTION",]
        """
    )
    Config.configure_task("my_task", print)
    Config.override(file_config.filename)

    assert len(Config.data_nodes) == 4
    assert type(Config.data_nodes["my_datanode"]) == DataNodeConfig
    assert type(Config.data_nodes["my_datanode2"]) == DataNodeConfig
    assert type(Config.data_nodes["my_datanode3"]) == DataNodeConfig
    assert Config.data_nodes["my_datanode"].path == "/data/csv"
    assert Config.data_nodes["my_datanode2"].path == "/data2/csv"
    assert Config.data_nodes["my_datanode3"].path == "/data3/csv"
    assert Config.data_nodes["my_datanode"].id == "my_datanode"
    assert Config.data_nodes["my_datanode2"].id == "my_datanode2"
    assert Config.data_nodes["my_datanode3"].id == "my_datanode3"
    assert Config.data_nodes["my_datanode"].validity_period == timedelta(1)
    assert Config.data_nodes["my_datanode3"].source == "local"

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

    assert len(Config.scenarios) == 2
    assert type(Config.scenarios["my_scenario"]) == ScenarioConfig
    assert Config.scenarios["my_scenario"].id == "my_scenario"
    assert Config.scenarios["my_scenario"].owner == "John Doe"
    assert len(Config.scenarios["my_scenario"].tasks) == 1
    assert type(Config.scenarios["my_scenario"].tasks[0]) == TaskConfig
    assert len(Config.scenarios["my_scenario"].additional_data_nodes) == 1
    assert type(Config.scenarios["my_scenario"].additional_data_nodes[0]) == DataNodeConfig
    assert Config.scenarios["my_scenario"].tasks[0].id == "my_task"
    assert Config.scenarios["my_scenario"].tasks[0].description == "task description"
    assert Config.scenarios["my_scenario"].additional_data_nodes[0].id == "my_datanode3"
    assert Config.scenarios["my_scenario"].additional_data_nodes[0].source == "local"
    assert [task.id for task in Config.scenarios["my_scenario"].sequences["sequence"]] == [
        Config.scenarios["my_scenario"].tasks[0].id
    ]
