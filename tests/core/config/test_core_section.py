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

from src.taipy.config import Config
from src.taipy.core import Core
from src.taipy.core._version._version_manager_factory import _VersionManagerFactory
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_core_section():
    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run()
    assert Config.core.mode == "development"
    assert Config.core.version_number == _VersionManagerFactory._build_manager()._get_development_version()
    assert not Config.core.force
    core.stop()

    with patch("sys.argv", ["prog"]):
        Config.configure_core(mode="experiment", version_number="test_num", force=True)
        core = Core()
        core.run()
    assert Config.core.mode == "experiment"
    assert Config.core.version_number == "test_num"
    assert Config.core.force
    core.stop()

    toml_config = NamedTemporaryFile(
        content="""
[TAIPY]

[CORE]
mode = "production"
version_number = "test_num_2"
force = "true:bool"
        """
    )
    Config.load(toml_config.filename)
    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run()
    assert Config.core.mode == "production"
    assert Config.core.version_number == "test_num_2"
    assert Config.core.force
    core.stop()

    with patch("sys.argv", ["prog", "--experiment", "test_num_3", "--no-taipy-force"]):
        core = Core()
        core.run()
        assert Config.core.mode == "experiment"
        assert Config.core.version_number == "test_num_3"
        assert not Config.core.force
        core.stop()


def test_clean_config():
    core_config = Config.configure_core(mode="experiment", version_number="test_num", force=True)

    assert Config.core is core_config

    core_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.core is core_config

    assert core_config.mode == "development"
    assert core_config.version_number == ""

    assert core_config.force is False
    assert core_config.properties == {}
