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

from copy import copy

import pytest

from taipy.common.config.checker.issue_collector import IssueCollector
from taipy.common.config.config import Config
from taipy.core.config import TaskConfig
from taipy.core.config.data_node_config import DataNodeConfig


class TestTaskConfigChecker:
    def test_check_config_id(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"].id = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        assert "config_id of TaskConfig `None` is empty" in caplog.text
        assert "function field of TaskConfig `new` is empty" in caplog.text
        assert len(Config._collector.warnings) == 2
        assert "inputs field of TaskConfig `new` is empty." in caplog.text
        assert "outputs field of TaskConfig `new` is empty." in caplog.text

        caplog.clear()

        config._sections[TaskConfig.name]["new"].id = "new"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert len(Config._collector.warnings) == 2

    def test_check_if_input_output_id_is_used_in_properties(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        input_dn_config = DataNodeConfig("input_dn")
        test_dn_config = DataNodeConfig("test")

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"].function = print
        config._sections[TaskConfig.name]["new"]._properties["test"] = "test"
        config._sections[TaskConfig.name]["new"]._inputs = [input_dn_config]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[TaskConfig.name]["new"]._inputs = [test_dn_config]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert (
            "The id of the DataNodeConfig `test` is overlapping with the property `test` of TaskConfig `new`."
            in caplog.text
        )

        config._sections[TaskConfig.name]["new"]._outputs = [test_dn_config]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        assert (
            "The id of the DataNodeConfig `test` is overlapping with the property `test` of TaskConfig `new`."
            in caplog.text
        )

    def test_check_config_id_is_different_from_all_task_properties(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])

        for conflict_id in [
            "additional_data_nodes",
            "config_id",
            "creation_date",
            "cycle",
            "data_nodes",
            "is_primary",
            "name",
            "owner_id",
            "properties",
            "sequences",
            "subscribers",
            "tags",
            "tasks",
            "version",
        ]:
            config._sections[TaskConfig.name]["new"].id = conflict_id

            with pytest.raises(SystemExit):
                Config._collector = IssueCollector()
                Config.check()
            assert len(Config._collector.errors) == 2
            expected_error_message = (
                "The id of the TaskConfig `new` is overlapping with the attribute"
                f" `{conflict_id}` of a Scenario entity."
            )
            assert expected_error_message in caplog.text

    def test_check_if_entity_property_key_used_is_predefined(self, caplog):
        Config._collector = IssueCollector()
        config = Config._applied_config
        Config._compile_configs()
        Config.check()
        assert len(Config._collector.errors) == 0

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"]._properties["_entity_owner"] = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        assert "function field of TaskConfig `new` is empty" in caplog.text
        assert "Properties of TaskConfig `default` cannot have `_entity_owner` as its property." in caplog.text

        caplog.clear()

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"]._properties["_entity_owner"] = "entity_owner"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 2
        assert "function field of TaskConfig `new` is empty" in caplog.text
        expected_error_message = (
            "Properties of TaskConfig `default` cannot have `_entity_owner` as its property."
            ' Current value of property `_entity_owner` is "entity_owner".'
        )
        assert expected_error_message in caplog.text

    def test_check_inputs(self, caplog):
        config = Config._applied_config
        Config._compile_configs()
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = config._sections[TaskConfig.name]["default"]
        config._sections[TaskConfig.name]["new"].id, config._sections[TaskConfig.name]["new"].function = "new", print
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 2
        assert "inputs field of TaskConfig `new` is empty." in caplog.text
        assert "outputs field of TaskConfig `new` is empty." in caplog.text

        config._sections[TaskConfig.name]["new"]._inputs = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "inputs field of TaskConfig `new` must be populated with a list of DataNodeConfig"
            " objects. Current value of property `inputs` is ['b', 'a', 'r']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._inputs = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "inputs field of TaskConfig `new` must be populated with a list of DataNodeConfig"
            " objects. Current value of property `inputs` is ['bar']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._inputs = [DataNodeConfig("bar")]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._inputs = ["bar", DataNodeConfig("bar")]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "inputs field of TaskConfig `new` must be populated with a list of"
            " DataNodeConfig objects. Current value of property `inputs` is"
            " ['bar', <taipy.core.config.data_node_config.DataNodeConfig object at"
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1

    def test_check_outputs(self, caplog):
        config = Config._applied_config
        Config._compile_configs()

        config._sections[TaskConfig.name]["default"]._outputs = "bar"
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = config._sections[TaskConfig.name]["default"]
        config._sections[TaskConfig.name]["new"].id, config._sections[TaskConfig.name]["new"].function = "new", print
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "outputs field of TaskConfig `new` must be populated with a list of DataNodeConfig"
            " objects. Current value of property `outputs` is ['b', 'a', 'r']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._outputs = ["bar"]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "outputs field of TaskConfig `new` must be populated with a list of DataNodeConfig"
            " objects. Current value of property `outputs` is ['bar']."
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._outputs = [DataNodeConfig("bar")]
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._outputs = ["bar", DataNodeConfig("bar")]
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "outputs field of TaskConfig `new` must be populated with a list of"
            " DataNodeConfig objects. Current value of property `outputs` is"
            " ['bar', <taipy.core.config.data_node_config.DataNodeConfig object at"
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 1

    def test_check_function(self, caplog):
        def mock_func():
            pass

        config = Config._applied_config
        Config._compile_configs()

        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"].id = "new"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "function field of TaskConfig `new` is empty." in caplog.text
        assert len(Config._collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].function = None
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        assert "function field of TaskConfig `new` is empty." in caplog.text
        assert len(Config._collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].function = "bar"
        with pytest.raises(SystemExit):
            Config._collector = IssueCollector()
            Config.check()
        assert len(Config._collector.errors) == 1
        expected_error_message = (
            "function field of TaskConfig `new` must be populated with Callable value."
            ' Current value of property `function` is "bar".'
        )
        assert expected_error_message in caplog.text
        assert len(Config._collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].function = mock_func
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.errors) == 0
        assert len(Config._collector.warnings) == 2
