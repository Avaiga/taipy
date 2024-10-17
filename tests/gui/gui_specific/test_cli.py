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

from unittest.mock import patch

from taipy.gui import Gui


def test_cli_port(gui: Gui):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
        assert gui._config.config.get("port") == 5000


def test_cli_port_1(gui: Gui):
    with patch("sys.argv", ["prog", "--port", "8080"]):
        gui.run(run_server=False)
        assert gui._config.config.get("port") == 8080


def test_cli_port_2(gui: Gui):
    with patch("sys.argv", ["prog", "-P", "9000"]):
        gui.run(run_server=False)
        assert gui._config.config.get("port") == 9000


def test_cli_port_auto(gui: Gui):
    with patch("sys.argv", ["prog", "--port", "auto"]):
        gui.run(run_server=False)
        assert gui._config.config.get("port") == "auto"


def test_cli_host(gui: Gui):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
        assert gui._config.config.get("host") == "127.0.0.1"


def test_cli_host_1(gui: Gui):
    with patch("sys.argv", ["prog", "--host", "localhost"]):
        gui.run(run_server=False)
        assert gui._config.config.get("host") == "localhost"


def test_cli_host_2(gui: Gui):
    with patch("sys.argv", ["prog", "-H", "localhost"]):
        gui.run(run_server=False)
        assert gui._config.config.get("host") == "localhost"


def test_taipy_debug(gui: Gui):
    with patch("sys.argv", ["prog", "--debug"]):
        gui.run(run_server=False, debug=False)
        assert gui._config.config.get("debug") is True


def test_taipy_no_debug(gui: Gui):
    with patch("sys.argv", ["prog", "--no-debug"]):
        gui.run(run_server=False, debug=True)
        assert gui._config.config.get("debug") is False


def test_taipy_reload(gui: Gui):
    with patch("sys.argv", ["prog", "--use-reloader"]):
        gui.run(run_server=False, use_reloader=False)
        assert gui._config.config.get("use_reloader") is True


def test_taipy_no_reload(gui: Gui):
    with patch("sys.argv", ["prog", "--no-reloader"]):
        gui.run(run_server=False, use_reloader=True)
        assert gui._config.config.get("use_reloader") is False


def test_ngrok_token(gui: Gui):
    with patch("sys.argv", ["prog", "--ngrok-token", "token"]):
        gui.run(run_server=False)
        assert gui._config.config.get("ngrok_token") == "token"


def test_webapp_path(gui: Gui):
    with patch("sys.argv", ["prog", "--webapp-path", "path"]):
        gui.run(run_server=False)
        assert gui._config.config.get("webapp_path") == "path"


def test_upload_folder(gui: Gui):
    with patch("sys.argv", ["prog", "--upload-folder", "folder"]):
        gui.run(run_server=False)
        assert gui._config.config.get("upload_folder") == "folder"


def test_client_url(gui: Gui):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
        assert gui._config.config.get("client_url") == "http://localhost:{port}"


def test_client_url_1(gui: Gui):
    with patch("sys.argv", ["prog", "--client-url", "url"]):
        gui.run(run_server=False)
        assert gui._config.config.get("client_url") == "url"
