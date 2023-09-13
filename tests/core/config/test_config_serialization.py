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

import datetime
import json

from src.taipy.core.config import CoreSection, DataNodeConfig, JobConfig, MigrationConfig, ScenarioConfig, TaskConfig
from taipy.config import Config
from taipy.config._serializer._json_serializer import _JsonSerializer
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def multiply(a):
    return a * 2


def migrate_csv_path(dn):
    dn.path = "foo.csv"


def compare_function(*data_node_results):
    comparison_result = {}
    current_result_index = 0
    for current_result in data_node_results:
        comparison_result[current_result_index] = {}
        next_result_index = 0
        for next_result in data_node_results:
            print(f"comparing result {current_result_index} with result {next_result_index}")
            comparison_result[current_result_index][next_result_index] = next_result - current_result
            next_result_index += 1
        current_result_index += 1
    return comparison_result


class CustomClass:
    a = None
    b = None


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            result = {"__type__": "Datetime", "__value__": o.isoformat()}
        else:
            result = json.JSONEncoder.default(self, o)
        return result


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source):
        if source.get("__type__") == "Datetime":
            return datetime.fromisoformat(source.get("__value__"))
        else:
            return source


def config_test_scenario():
    test_csv_dn_cfg = Config.configure_csv_data_node(
        id="test_csv_dn",
        path="./test.csv",
        exposed_type=CustomClass,
        scope=Scope.GLOBAL,
        validity_period=datetime.timedelta(1),
    )

    test_json_dn_cfg = Config.configure_json_data_node(
        id="test_json_dn",
        default_path="./test.json",
        encoder=CustomEncoder,
        decoder=CustomDecoder,
    )

    test_pickle_dn_cfg = Config.configure_pickle_data_node(
        id="test_pickle_dn",
        path="./test.p",
        scope=Scope.SCENARIO,
        validity_period=datetime.timedelta(1),
    )

    test_task_cfg = Config.configure_task(
        id="test_task", input=test_csv_dn_cfg, function=multiply, output=test_json_dn_cfg
    )

    test_scenario_cfg = Config.configure_scenario(
        id="test_scenario",
        task_configs=[test_task_cfg],
        additional_data_node_configs=[test_pickle_dn_cfg],
        comparators={test_json_dn_cfg.id: compare_function},
        frequency=Frequency.DAILY,
    )
    test_scenario_cfg.add_sequences({"sequence1": [test_task_cfg]})

    Config.add_migration_function("1.0", test_csv_dn_cfg, migrate_csv_path)

    return test_scenario_cfg


def test_read_write_toml_configuration_file():
    expected_toml_config = """
[TAIPY]

[JOB]
mode = "development"
max_nb_of_workers = "1:int"

[CORE]
root_folder = "./taipy/"
storage_folder = ".data/"
repository_type = "filesystem"
read_entity_retry = "0:int"
mode = "development"
version_number = ""
force = "False:bool"
core_version="3.0.0"

[DATA_NODE.default]
storage_type = "pickle"
scope = "SCENARIO:SCOPE"

[DATA_NODE.test_csv_dn]
storage_type = "csv"
scope = "GLOBAL:SCOPE"
validity_period = "1d0h0m0s:timedelta"
path = "./test.csv"
exposed_type = "tests.core.config.test_config_serialization.CustomClass:class"
encoding = "utf-8"
has_header = "True:bool"

[DATA_NODE.test_json_dn]
storage_type = "json"
scope = "SCENARIO:SCOPE"
default_path = "./test.json"
encoder = "tests.core.config.test_config_serialization.CustomEncoder:class"
decoder = "tests.core.config.test_config_serialization.CustomDecoder:class"
encoding = "utf-8"

[DATA_NODE.test_pickle_dn]
storage_type = "pickle"
scope = "SCENARIO:SCOPE"
validity_period = "1d0h0m0s:timedelta"
path = "./test.p"

[TASK.default]
inputs = []
outputs = []
skippable = "False:bool"

[TASK.test_task]
function = "tests.core.config.test_config_serialization.multiply:function"
inputs = [ "test_csv_dn:SECTION",]
outputs = [ "test_json_dn:SECTION",]
skippable = "False:bool"

[SCENARIO.default]
tasks = []
additional_data_nodes = []

[SCENARIO.test_scenario]
tasks = [ "test_task:SECTION",]
additional_data_nodes = [ "test_pickle_dn:SECTION",]
frequency = "DAILY:FREQUENCY"

[VERSION_MIGRATION.migration_fcts."1.0"]
test_csv_dn = "tests.core.config.test_config_serialization.migrate_csv_path:function"

[SCENARIO.default.comparators]

[SCENARIO.default.sequences]

[SCENARIO.test_scenario.comparators]
test_json_dn = [ "tests.core.config.test_config_serialization.compare_function:function",]

[SCENARIO.test_scenario.sequences]
sequence1 = [ "test_task:SECTION",]
""".strip()

    config_test_scenario()

    tf = NamedTemporaryFile()
    Config.backup(tf.filename)
    actual_config = tf.read().strip()
    assert actual_config == expected_toml_config

    Config.load(tf.filename)
    tf2 = NamedTemporaryFile()
    Config.backup(tf2.filename)

    actual_config_2 = tf2.read().strip()
    assert actual_config_2 == expected_toml_config

    assert Config.unique_sections is not None
    assert len(Config.unique_sections) == 3

    assert Config.unique_sections[JobConfig.name].mode == "development"
    assert Config.unique_sections[JobConfig.name].max_nb_of_workers == 1

    assert Config.unique_sections[MigrationConfig.name].migration_fcts["1.0"] == {"test_csv_dn": migrate_csv_path}

    assert Config.sections is not None
    assert len(Config.sections) == 3

    assert Config.sections[DataNodeConfig.name] is not None
    assert len(Config.sections[DataNodeConfig.name]) == 4
    assert Config.sections[DataNodeConfig.name]["default"] is not None
    assert Config.sections[DataNodeConfig.name]["default"].storage_type == "pickle"
    assert Config.sections[DataNodeConfig.name]["default"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].storage_type == "csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].scope == Scope.GLOBAL
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].validity_period == datetime.timedelta(1)
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].has_header is True
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].path == "./test.csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].encoding == "utf-8"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].exposed_type == CustomClass
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].storage_type == "json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].default_path == "./test.json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].encoding == "utf-8"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].encoder == CustomEncoder
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].decoder == CustomDecoder
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].storage_type == "pickle"
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].validity_period == datetime.timedelta(1)
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].path == "./test.p"

    assert Config.sections[TaskConfig.name] is not None
    assert len(Config.sections[TaskConfig.name]) == 2
    assert Config.sections[TaskConfig.name]["default"] is not None
    assert Config.sections[TaskConfig.name]["default"].inputs == []
    assert Config.sections[TaskConfig.name]["default"].outputs == []
    assert Config.sections[TaskConfig.name]["default"].function is None
    assert not Config.sections[TaskConfig.name]["default"].skippable
    assert [inp.id for inp in Config.sections[TaskConfig.name]["test_task"].inputs] == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id
    ]
    assert [outp.id for outp in Config.sections[TaskConfig.name]["test_task"].outputs] == [
        Config.sections[DataNodeConfig.name]["test_json_dn"].id
    ]
    assert Config.sections[TaskConfig.name]["test_task"].function == multiply
    assert Config.sections[TaskConfig.name]["test_task"].function == multiply

    assert Config.sections[ScenarioConfig.name] is not None
    assert len(Config.sections[ScenarioConfig.name]) == 2
    assert Config.sections[ScenarioConfig.name]["default"] is not None
    assert Config.sections[ScenarioConfig.name]["default"].tasks == []
    assert Config.sections[ScenarioConfig.name]["default"].additional_data_nodes == []
    assert Config.sections[ScenarioConfig.name]["default"].data_nodes == []
    assert len(Config.sections[ScenarioConfig.name]["default"].comparators) == 0
    assert [task.id for task in Config.sections[ScenarioConfig.name]["test_scenario"].tasks] == [
        Config.sections[TaskConfig.name]["test_task"].id
    ]
    assert [
        additional_data_node.id
        for additional_data_node in Config.sections[ScenarioConfig.name]["test_scenario"].additional_data_nodes
    ] == [Config.sections[DataNodeConfig.name]["test_pickle_dn"].id]
    assert sorted([data_node.id for data_node in Config.sections[ScenarioConfig.name]["test_scenario"].data_nodes]) == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id,
        Config.sections[DataNodeConfig.name]["test_json_dn"].id,
        Config.sections[DataNodeConfig.name]["test_pickle_dn"].id,
    ]
    sequences = {}
    for sequence_name, sequence_tasks in Config.sections[ScenarioConfig.name]["test_scenario"].sequences.items():
        sequences[sequence_name] = [task.id for task in sequence_tasks]
    assert sequences == {"sequence1": [Config.sections[TaskConfig.name]["test_task"].id]}

    assert dict(Config.sections[ScenarioConfig.name]["test_scenario"].comparators) == {
        "test_json_dn": [compare_function]
    }


def test_read_write_json_configuration_file():
    expected_json_config = """
{
"TAIPY": {},
"JOB": {
"mode": "development",
"max_nb_of_workers": "1:int"
},
"CORE": {
"root_folder": "./taipy/",
"storage_folder": ".data/",
"repository_type": "filesystem",
"read_entity_retry": "0:int",
"mode": "development",
"version_number": "",
"force": "False:bool"
},
"VERSION_MIGRATION": {
"migration_fcts": {
"1.0": {
"test_csv_dn": "tests.core.config.test_config_serialization.migrate_csv_path:function"
}
}
},
"DATA_NODE": {
"default": {
"storage_type": "pickle",
"scope": "SCENARIO:SCOPE"
},
"test_csv_dn": {
"storage_type": "csv",
"scope": "GLOBAL:SCOPE",
"validity_period": "1d0h0m0s:timedelta",
"path": "./test.csv",
"exposed_type": "tests.core.config.test_config_serialization.CustomClass:class",
"encoding": "utf-8",
"has_header": "True:bool"
},
"test_json_dn": {
"storage_type": "json",
"scope": "SCENARIO:SCOPE",
"default_path": "./test.json",
"encoder": "tests.core.config.test_config_serialization.CustomEncoder:class",
"decoder": "tests.core.config.test_config_serialization.CustomDecoder:class",
"encoding": "utf-8"
},
"test_pickle_dn": {
"storage_type": "pickle",
"scope": "SCENARIO:SCOPE",
"validity_period": "1d0h0m0s:timedelta",
"path": "./test.p"
}
},
"TASK": {
"default": {
"function": null,
"inputs": [],
"outputs": [],
"skippable": "False:bool"
},
"test_task": {
"function": "tests.core.config.test_config_serialization.multiply:function",
"inputs": [
"test_csv_dn:SECTION"
],
"outputs": [
"test_json_dn:SECTION"
],
"skippable": "False:bool"
}
},
"SCENARIO": {
"default": {
"comparators": {},
"tasks": [],
"additional_data_nodes": [],
"frequency": null,
"sequences": {}
},
"test_scenario": {
"comparators": {
"test_json_dn": [
"tests.core.config.test_config_serialization.compare_function:function"
]
},
"tasks": [
"test_task:SECTION"
],
"additional_data_nodes": [
"test_pickle_dn:SECTION"
],
"frequency": "DAILY:FREQUENCY",
"sequences": {
"sequence1": [
"test_task:SECTION"
]
}
}
}
}
    """.strip()

    Config._serializer = _JsonSerializer()
    config_test_scenario()

    tf = NamedTemporaryFile()
    Config.backup(tf.filename)
    actual_config = tf.read().strip()
    assert actual_config == expected_json_config

    Config.load(tf.filename)
    tf2 = NamedTemporaryFile()
    Config.backup(tf2.filename)

    actual_config_2 = tf2.read().strip()
    assert actual_config_2 == expected_json_config

    assert Config.unique_sections is not None
    assert len(Config.unique_sections) == 3

    assert Config.unique_sections[JobConfig.name].mode == "development"
    assert Config.unique_sections[JobConfig.name].max_nb_of_workers == 1

    assert Config.unique_sections[MigrationConfig.name].migration_fcts["1.0"] == {"test_csv_dn": migrate_csv_path}

    assert Config.sections is not None
    assert len(Config.sections) == 3

    assert Config.sections[DataNodeConfig.name] is not None
    assert len(Config.sections[DataNodeConfig.name]) == 4
    assert Config.sections[DataNodeConfig.name]["default"] is not None
    assert Config.sections[DataNodeConfig.name]["default"].storage_type == "pickle"
    assert Config.sections[DataNodeConfig.name]["default"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].storage_type == "csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].scope == Scope.GLOBAL
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].validity_period == datetime.timedelta(1)
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].has_header is True
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].path == "./test.csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].encoding == "utf-8"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].exposed_type == CustomClass
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].storage_type == "json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].default_path == "./test.json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].encoding == "utf-8"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].encoder == CustomEncoder
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].decoder == CustomDecoder
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].storage_type == "pickle"
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].validity_period == datetime.timedelta(1)
    assert Config.sections[DataNodeConfig.name]["test_pickle_dn"].path == "./test.p"

    assert Config.sections[TaskConfig.name] is not None
    assert len(Config.sections[TaskConfig.name]) == 2
    assert Config.sections[TaskConfig.name]["default"] is not None
    assert Config.sections[TaskConfig.name]["default"].inputs == []
    assert Config.sections[TaskConfig.name]["default"].outputs == []
    assert Config.sections[TaskConfig.name]["default"].function is None
    assert [inp.id for inp in Config.sections[TaskConfig.name]["test_task"].inputs] == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id
    ]
    assert [outp.id for outp in Config.sections[TaskConfig.name]["test_task"].outputs] == [
        Config.sections[DataNodeConfig.name]["test_json_dn"].id
    ]
    assert Config.sections[TaskConfig.name]["test_task"].function == multiply

    assert Config.sections[ScenarioConfig.name] is not None
    assert len(Config.sections[ScenarioConfig.name]) == 2
    assert Config.sections[ScenarioConfig.name]["default"] is not None
    assert Config.sections[ScenarioConfig.name]["default"].tasks == []
    assert Config.sections[ScenarioConfig.name]["default"].additional_data_nodes == []
    assert Config.sections[ScenarioConfig.name]["default"].data_nodes == []
    assert len(Config.sections[ScenarioConfig.name]["default"].comparators) == 0
    assert [task.id for task in Config.sections[ScenarioConfig.name]["test_scenario"].tasks] == [
        Config.sections[TaskConfig.name]["test_task"].id
    ]
    assert [
        additional_data_node.id
        for additional_data_node in Config.sections[ScenarioConfig.name]["test_scenario"].additional_data_nodes
    ] == [Config.sections[DataNodeConfig.name]["test_pickle_dn"].id]
    assert sorted([data_node.id for data_node in Config.sections[ScenarioConfig.name]["test_scenario"].data_nodes]) == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id,
        Config.sections[DataNodeConfig.name]["test_json_dn"].id,
        Config.sections[DataNodeConfig.name]["test_pickle_dn"].id,
    ]
    sequences = {}
    for sequence_name, sequence_tasks in Config.sections[ScenarioConfig.name]["test_scenario"].sequences.items():
        sequences[sequence_name] = [task.id for task in sequence_tasks]
    assert sequences == {"sequence1": [Config.sections[TaskConfig.name]["test_task"].id]}

    assert dict(Config.sections[ScenarioConfig.name]["test_scenario"].comparators) == {
        "test_json_dn": [compare_function]
    }


def test_read_write_toml_configuration_file_migrate_sequence_in_scenario():
    old_toml_config = """
[TAIPY]

[JOB]
mode = "development"
max_nb_of_workers = "1:int"

[CORE]
root_folder = "./taipy/"
storage_folder = ".data/"
repository_type = "filesystem"
mode = "development"
version_number = ""
force = "False:bool"

[DATA_NODE.default]
storage_type = "pickle"
scope = "SCENARIO:SCOPE"

[DATA_NODE.test_csv_dn]
storage_type = "csv"
scope = "GLOBAL:SCOPE"
validity_period = "1d0h0m0s:timedelta"
path = "./test.csv"
exposed_type = "tests.core.config.test_config_serialization.CustomClass:class"
has_header = "True:bool"

[DATA_NODE.test_json_dn]
storage_type = "json"
scope = "SCENARIO:SCOPE"
default_path = "./test.json"
encoder = "tests.core.config.test_config_serialization.CustomEncoder:class"
decoder = "tests.core.config.test_config_serialization.CustomDecoder:class"

[TASK.default]
inputs = []
outputs = []
skippable = "False:bool"

[TASK.test_task]
function = "tests.core.config.test_config_serialization.multiply:function"
inputs = [ "test_csv_dn:SECTION",]
outputs = [ "test_json_dn:SECTION",]
skippable = "False:bool"

[SCENARIO.default]

[SCENARIO.test_scenario]
tasks = [ "test_task:SECTION",]
sequences.test_sequence = [ "test_task:SECTION",]
frequency = "DAILY:FREQUENCY"

[VERSION_MIGRATION.migration_fcts."1.0"]
test_csv_dn = "tests.core.config.test_config_serialization.migrate_csv_path:function"

[SCENARIO.default.comparators]

[SCENARIO.test_scenario.comparators]
test_json_dn = [ "tests.core.config.test_config_serialization.compare_function:function",]
    """.strip()

    config_test_scenario()

    tf = NamedTemporaryFile()
    with open(tf.filename, "w") as fd:
        fd.writelines(old_toml_config)
    Config.restore(tf.filename)

    assert Config.unique_sections is not None
    assert len(Config.unique_sections) == 3

    assert Config.unique_sections[CoreSection.name].root_folder == "./taipy/"
    assert Config.unique_sections[CoreSection.name].storage_folder == ".data/"
    assert Config.unique_sections[CoreSection.name].repository_type == "filesystem"
    assert Config.unique_sections[CoreSection.name].repository_properties == {}
    assert Config.unique_sections[CoreSection.name].mode == "development"
    assert Config.unique_sections[CoreSection.name].version_number == ""
    assert Config.unique_sections[CoreSection.name].force is False

    assert Config.unique_sections[JobConfig.name].mode == "development"
    assert Config.unique_sections[JobConfig.name].max_nb_of_workers == 1

    assert Config.unique_sections[MigrationConfig.name].migration_fcts["1.0"] == {"test_csv_dn": migrate_csv_path}

    assert Config.sections is not None
    assert len(Config.sections) == 3

    assert Config.sections[DataNodeConfig.name] is not None
    assert len(Config.sections[DataNodeConfig.name]) == 3
    assert Config.sections[DataNodeConfig.name]["default"] is not None
    assert Config.sections[DataNodeConfig.name]["default"].storage_type == "pickle"
    assert Config.sections[DataNodeConfig.name]["default"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].storage_type == "csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].scope == Scope.GLOBAL
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].validity_period == datetime.timedelta(1)
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].has_header is True
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].path == "./test.csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].exposed_type == CustomClass
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].storage_type == "json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].default_path == "./test.json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].encoder == CustomEncoder
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].decoder == CustomDecoder

    assert Config.sections[TaskConfig.name] is not None
    assert len(Config.sections[TaskConfig.name]) == 2
    assert Config.sections[TaskConfig.name]["default"] is not None
    assert Config.sections[TaskConfig.name]["default"].inputs == []
    assert Config.sections[TaskConfig.name]["default"].outputs == []
    assert Config.sections[TaskConfig.name]["default"].function is None
    assert not Config.sections[TaskConfig.name]["default"].skippable
    assert [inp.id for inp in Config.sections[TaskConfig.name]["test_task"].inputs] == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id
    ]
    assert [outp.id for outp in Config.sections[TaskConfig.name]["test_task"].outputs] == [
        Config.sections[DataNodeConfig.name]["test_json_dn"].id
    ]
    assert Config.sections[TaskConfig.name]["test_task"].function == multiply
    assert Config.sections[TaskConfig.name]["test_task"].function == multiply

    assert Config.sections[ScenarioConfig.name] is not None
    assert len(Config.sections[ScenarioConfig.name]) == 2
    assert Config.sections[ScenarioConfig.name]["default"] is not None
    assert Config.sections[ScenarioConfig.name]["default"].tasks == []
    assert Config.sections[ScenarioConfig.name]["default"].additional_data_nodes == []
    assert Config.sections[ScenarioConfig.name]["default"].data_nodes == []
    assert len(Config.sections[ScenarioConfig.name]["default"].comparators) == 0
    assert [task.id for task in Config.sections[ScenarioConfig.name]["test_scenario"].tasks] == [
        Config.sections[TaskConfig.name]["test_task"].id
    ]
    assert [
        additional_data_node.id
        for additional_data_node in Config.sections[ScenarioConfig.name]["test_scenario"].additional_data_nodes
    ] == []
    assert sorted([data_node.id for data_node in Config.sections[ScenarioConfig.name]["test_scenario"].data_nodes]) == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id,
        Config.sections[DataNodeConfig.name]["test_json_dn"].id,
    ]
    assert Config.sections[ScenarioConfig.name]["test_scenario"].sequences == {
        "test_sequence": [Config.sections[TaskConfig.name]["test_task"]]
    }

    assert dict(Config.sections[ScenarioConfig.name]["test_scenario"].comparators) == {
        "test_json_dn": [compare_function]
    }


def test_read_write_json_configuration_file_migrate_sequence_in_scenario():
    old_json_config = """
{
"TAIPY": {},
"JOB": {
"mode": "development",
"max_nb_of_workers": "1:int"
},
"CORE": {
"root_folder": "./taipy/",
"storage_folder": ".data/",
"repository_type": "filesystem",
"read_entity_retry": "0:int",
"mode": "development",
"version_number": "",
"force": "False:bool"
},
"VERSION_MIGRATION": {
"migration_fcts": {
"1.0": {
"test_csv_dn": "tests.core.config.test_config_serialization.migrate_csv_path:function"
}
}
},
"DATA_NODE": {
"default": {
"storage_type": "pickle",
"scope": "SCENARIO:SCOPE"
},
"test_csv_dn": {
"storage_type": "csv",
"scope": "GLOBAL:SCOPE",
"validity_period": "1d0h0m0s:timedelta",
"path": "./test.csv",
"exposed_type": "tests.core.config.test_config_serialization.CustomClass:class",
"has_header": "True:bool"
},
"test_json_dn": {
"storage_type": "json",
"scope": "SCENARIO:SCOPE",
"default_path": "./test.json",
"encoder": "tests.core.config.test_config_serialization.CustomEncoder:class",
"decoder": "tests.core.config.test_config_serialization.CustomDecoder:class"
}
},
"TASK": {
"default": {
"function": null,
"inputs": [],
"outputs": [],
"skippable": "False:bool"
},
"test_task": {
"function": "tests.core.config.test_config_serialization.multiply:function",
"inputs": [
"test_csv_dn:SECTION"
],
"outputs": [
"test_json_dn:SECTION"
],
"skippable": "False:bool"
}
},
"SCENARIO": {
"default": {
"comparators": {},
"sequences": {},
"frequency": null
},
"test_scenario": {
"comparators": {
"test_json_dn": [
"tests.core.config.test_config_serialization.compare_function:function"
]
},
"tasks": [
"test_task:SECTION"
],
"sequences": {
"test_sequence": [
"test_task:SECTION"
]
},
"frequency": "DAILY:FREQUENCY"
}
}
}
    """.strip()

    Config._serializer = _JsonSerializer()
    config_test_scenario()

    tf = NamedTemporaryFile()
    with open(tf.filename, "w") as fd:
        fd.writelines(old_json_config)
    Config.restore(tf.filename)

    assert Config.unique_sections is not None
    assert len(Config.unique_sections) == 3

    assert Config.unique_sections[CoreSection.name].root_folder == "./taipy/"
    assert Config.unique_sections[CoreSection.name].storage_folder == ".data/"
    assert Config.unique_sections[CoreSection.name].repository_type == "filesystem"
    assert Config.unique_sections[CoreSection.name].repository_properties == {}
    assert Config.unique_sections[CoreSection.name].mode == "development"
    assert Config.unique_sections[CoreSection.name].version_number == ""
    assert Config.unique_sections[CoreSection.name].force is False

    assert Config.unique_sections[JobConfig.name].mode == "development"
    assert Config.unique_sections[JobConfig.name].max_nb_of_workers == 1

    assert Config.unique_sections[MigrationConfig.name].migration_fcts["1.0"] == {"test_csv_dn": migrate_csv_path}

    assert Config.sections is not None
    assert len(Config.sections) == 3

    assert Config.sections[DataNodeConfig.name] is not None
    assert len(Config.sections[DataNodeConfig.name]) == 3
    assert Config.sections[DataNodeConfig.name]["default"] is not None
    assert Config.sections[DataNodeConfig.name]["default"].storage_type == "pickle"
    assert Config.sections[DataNodeConfig.name]["default"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].storage_type == "csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].scope == Scope.GLOBAL
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].validity_period == datetime.timedelta(1)
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].has_header is True
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].path == "./test.csv"
    assert Config.sections[DataNodeConfig.name]["test_csv_dn"].exposed_type == CustomClass
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].storage_type == "json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].scope == Scope.SCENARIO
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].default_path == "./test.json"
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].encoder == CustomEncoder
    assert Config.sections[DataNodeConfig.name]["test_json_dn"].decoder == CustomDecoder

    assert Config.sections[TaskConfig.name] is not None
    assert len(Config.sections[TaskConfig.name]) == 2
    assert Config.sections[TaskConfig.name]["default"] is not None
    assert Config.sections[TaskConfig.name]["default"].inputs == []
    assert Config.sections[TaskConfig.name]["default"].outputs == []
    assert Config.sections[TaskConfig.name]["default"].function is None
    assert [inp.id for inp in Config.sections[TaskConfig.name]["test_task"].inputs] == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id
    ]
    assert [outp.id for outp in Config.sections[TaskConfig.name]["test_task"].outputs] == [
        Config.sections[DataNodeConfig.name]["test_json_dn"].id
    ]
    assert Config.sections[TaskConfig.name]["test_task"].function == multiply

    assert Config.sections[ScenarioConfig.name] is not None
    assert len(Config.sections[ScenarioConfig.name]) == 2
    assert Config.sections[ScenarioConfig.name]["default"] is not None
    assert Config.sections[ScenarioConfig.name]["default"].tasks == []
    assert Config.sections[ScenarioConfig.name]["default"].additional_data_nodes == []
    assert Config.sections[ScenarioConfig.name]["default"].data_nodes == []
    assert len(Config.sections[ScenarioConfig.name]["default"].comparators) == 0
    assert [task.id for task in Config.sections[ScenarioConfig.name]["test_scenario"].tasks] == [
        Config.sections[TaskConfig.name]["test_task"].id
    ]
    assert [
        additional_data_node.id
        for additional_data_node in Config.sections[ScenarioConfig.name]["test_scenario"].additional_data_nodes
    ] == []
    assert sorted([data_node.id for data_node in Config.sections[ScenarioConfig.name]["test_scenario"].data_nodes]) == [
        Config.sections[DataNodeConfig.name]["test_csv_dn"].id,
        Config.sections[DataNodeConfig.name]["test_json_dn"].id,
    ]
    assert Config.sections[ScenarioConfig.name]["test_scenario"].sequences == {
        "test_sequence": [Config.sections[TaskConfig.name]["test_task"]]
    }

    assert dict(Config.sections[ScenarioConfig.name]["test_scenario"].comparators) == {
        "test_json_dn": [compare_function]
    }
