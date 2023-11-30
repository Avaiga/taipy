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

from unittest.mock import patch

import pytest

from src.taipy.core import Core
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.config import MigrationConfig
from taipy.config.config import Config


def mock_func():
    pass


def test_check_if_entity_property_key_used_is_predefined(caplog):
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        core = Core()
        core.run()
    assert caplog.text == ""
    core.stop()

    caplog.clear()

    Config.unique_sections[MigrationConfig.name]._properties["_entity_owner"] = None
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        with pytest.raises(SystemExit):
            core = Core()
            core.run()
        core.stop()
    assert (
        "Properties of MigrationConfig `VERSION_MIGRATION` cannot have `_entity_owner` as its property." in caplog.text
    )

    caplog.clear()

    Config.unique_sections[MigrationConfig.name]._properties["_entity_owner"] = "entity_owner"
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        with pytest.raises(SystemExit):
            core = Core()
            core.run()
        core.stop()
    expected_error_message = (
        "Properties of MigrationConfig `VERSION_MIGRATION` cannot have `_entity_owner` as its property."
        ' Current value of property `_entity_owner` is "entity_owner".'
    )
    assert expected_error_message in caplog.text


def test_check_valid_version(caplog):
    data_nodes1 = Config.configure_data_node("data_nodes1", "pickle")

    Config.add_migration_function("2.0", data_nodes1, mock_func)
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        with pytest.raises(SystemExit):
            core = Core()
            core.run()
        core.stop()
    assert "The target version for a migration function must be a production version." in caplog.text

    caplog.clear()
    Config.unblock_update()

    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()
    assert caplog.text == ""
    core.stop()


def test_check_callable_function(caplog):
    data_nodes1 = Config.configure_data_node("data_nodes1", "pickle")
    Config.add_migration_function("1.0", data_nodes1, 1)
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        with pytest.raises(SystemExit):
            core = Core()
            core.run()
        core.stop()
    expected_error_message = (
        "The migration function of config `data_nodes1` from version 1.0 must be populated with"
        " Callable value. Current value of property `migration_fcts` is 1."
    )
    assert expected_error_message in caplog.text

    caplog.clear()
    Config.unblock_update()

    Config.add_migration_function("1.0", data_nodes1, "bar")
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        with pytest.raises(SystemExit):
            core = Core()
            core.run()
        core.stop()
    expected_error_message = (
        "The migration function of config `data_nodes1` from version 1.0 must be populated with"
        ' Callable value. Current value of property `migration_fcts` is "bar".'
    )
    assert expected_error_message in caplog.text

    caplog.clear()
    Config.unblock_update()

    Config.add_migration_function("1.0", data_nodes1, mock_func)
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        core = Core()
        core.run()
        core.stop()


def test_check_migration_from_productions_to_productions_exist(caplog):
    _VersionManager._set_production_version("1.0", True)
    _VersionManager._set_production_version("1.1", True)
    _VersionManager._set_production_version("1.2", True)

    with patch("sys.argv", ["prog", "--production", "1.0"]):
        core = Core()
        core.run()
        core.stop()
    assert 'There is no migration function from production version "1.0" to version "1.1".' in caplog.text
    assert 'There is no migration function from production version "1.1" to version "1.2".' in caplog.text

    caplog.clear()
    Config.unblock_update()

    Config.add_migration_function("1.2", "data_nodes1", mock_func)
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        core = Core()
        core.run()
        core.stop()
    assert 'There is no migration function from production version "1.0" to version "1.1".' in caplog.text
