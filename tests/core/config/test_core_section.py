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

from src.taipy.core import Core
from taipy import Config
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_core_section():
    core = Core()
    core.run()
    assert Config.core.mode == "development"
    assert Config.core.version_number == ""
    assert not Config.core.force
    assert not Config.core.clean_entities
    core.stop()

    Config.configure_core(mode="experiment", version_number="test_num", force=True, clean_entities=True)
    core = Core()
    core.run()
    assert Config.core.mode == "experiment"
    assert Config.core.version_number == "test_num"
    assert Config.core.force
    assert Config.core.clean_entities
    core.stop()

    toml_config = NamedTemporaryFile(
        content="""
[TAIPY]

[core]
mode = "production"
version_number = "test_num_2"
taipy_force = "true:bool"
clean_entities = "false:bool"
        """
    )
    Config.load(toml_config.filename)
    core = Core()
    core.run()
    assert Config.core.mode == "production"
    assert Config.core.version_number == "test_num_2"
    assert Config.core.force
    assert not Config.core.clean_entities
    core.stop()

    with patch("sys.argv", ["prog", "--experiment", "test_num_3", "--no-taipy-force", "--clean-entities"]):
        core = Core()
        core.run()
        assert Config.core.mode == "experiment"
        assert Config.core.version_number == "test_num_3"
        assert not Config.core.force
        assert Config.core.clean_entities
        core.stop()
