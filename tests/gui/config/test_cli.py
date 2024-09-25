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
import tempfile
from unittest.mock import patch

import pytest

from taipy.common.config import Config, _inject_section
from taipy.gui import Gui
from taipy.gui._default_config import default_config
from taipy.gui._gui_section import _GuiSection


class NamedTemporaryFile:
    def __init__(self, content=None):
        with tempfile.NamedTemporaryFile("w", delete=False) as fd:
            if content:
                fd.write(content)
            self.filename = fd.name

    def read(self):
        with open(self.filename, "r") as fp:
            return fp.read()

    def __del__(self):
        os.unlink(self.filename)


@pytest.fixture
def init_config(reset_configuration_singleton):
    def _init_config():
        reset_configuration_singleton()

        _inject_section(
            _GuiSection,
            "gui_config",
            _GuiSection(property_list=list(default_config)),
            [("configure_gui", _GuiSection._configure)],
            add_to_unconflicted_sections=True,
        )

    return _init_config


@pytest.fixture(scope="function", autouse=True)
def cleanup_test(helpers, init_config):
    init_config()
    helpers.test_cleanup()
    yield
    init_config()
    helpers.test_cleanup()


def test_gui_service_arguments_hierarchy():
    # Test default configuration
    gui = Gui()
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    service_config = gui._config.config
    assert not service_config["allow_unsafe_werkzeug"]
    assert service_config["async_mode"] == "gevent"
    assert service_config["change_delay"] is None
    assert service_config["chart_dark_template"] is None
    assert service_config["dark_mode"]
    assert service_config["dark_theme"] is None
    assert not service_config["debug"]
    assert not service_config["extended_status"]
    assert service_config["favicon"] is None
    assert not service_config["flask_log"]
    assert service_config["host"] == "127.0.0.1"
    assert service_config["light_theme"] is None
    assert service_config["margin"] is None
    assert service_config["ngrok_token"] == ""
    assert service_config["notification_duration"] == 3000
    assert service_config["port"] == 5000
    assert service_config["propagate"]
    assert service_config["run_browser"]
    assert not service_config["run_in_thread"]
    assert not service_config["run_server"]
    assert not service_config["single_client"]
    assert service_config["state_retention_period"] == 0
    assert not service_config["system_notification"]
    assert service_config["theme"] is None
    assert service_config["time_zone"] is None
    assert service_config["title"] is None
    assert service_config["upload_folder"] is None
    assert not service_config["use_arrow"]
    assert not service_config["use_reloader"]
    assert service_config["watermark"] == "Taipy inside"
    assert service_config["webapp_path"] is None
    gui.stop()

    # Override default configuration by explicit defined arguments in Gui.run()
    gui = Gui()
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, watermark="", host="my_host", port=5001)
    service_config = gui._config.config
    assert service_config["watermark"] == ""
    assert service_config["host"] == "my_host"
    assert service_config["port"] == 5001
    gui.stop()

    # Override Gui.run() arguments by explicit defined arguments in Config.configure_gui()
    Config.configure_gui(dark_mode=False, host="my_2nd_host", port=5002)
    gui = Gui()
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, watermark="", host="my_host", port=5001)
    service_config = gui._config.config
    assert not service_config["dark_mode"]
    assert service_config["host"] == "my_2nd_host"
    assert service_config["watermark"] == ""
    assert service_config["port"] == 5002
    gui.stop()

    # Override Config.configure_gui() arguments by loading a TOML file with [gui] section
    toml_config = NamedTemporaryFile(
        content="""
[TAIPY]

[gui]
host = "my_3rd_host"
port = 5003
use_reloader = "true:bool"
    """
    )
    Config.load(toml_config.filename)
    gui = Gui()
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, host="my_host", port=5001)
    service_config = gui._config.config
    assert service_config["host"] == "my_3rd_host"
    assert service_config["port"] == 5003
    assert service_config["use_reloader"]
    gui.stop()

    # Override TOML configuration file with CLI arguments
    with patch("sys.argv", ["prog", "--host", "my_4th_host", "--port", "5004", "--no-reloader", "--debug"]):
        gui = Gui()
        gui.run(run_server=False, host="my_host", port=5001)
        service_config = gui._config.config
        assert service_config["host"] == "my_4th_host"
        assert service_config["port"] == 5004
        assert not service_config["use_reloader"]
        assert service_config["debug"]
        gui.stop()


def test_clean_config():
    gui_config = Config.configure_gui(dark_mode=False)

    assert Config.gui_config is gui_config

    gui_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.gui_config is gui_config

    assert gui_config.dark_mode is None
    assert gui_config.properties == {}
