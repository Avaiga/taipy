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

from taipy._cli._base_cli import _CLI


class _GuiCLI:
    """Command-line interface of GUI."""

    @classmethod
    def create_parser(cls):
        gui_parser = _CLI._add_groupparser("Taipy GUI", "Optional arguments for Taipy GUI service")

        gui_parser.add_argument("-P", "--port", nargs="?", default="", const="", help="Specify server port")
        gui_parser.add_argument("-H", "--host", nargs="?", default="", const="", help="Specify server host")

        gui_parser.add_argument("--ngrok-token", nargs="?", default="", const="", help="Specify NGROK Authtoken")
        gui_parser.add_argument(
            "--webapp-path",
            nargs="?",
            default="",
            const="",
            help="The path to the web app to be used. The default is the webapp directory under gui in the Taipy GUI package directory.",
        )

        debug_group = gui_parser.add_mutually_exclusive_group()
        debug_group.add_argument("--debug", help="Turn on debug", action="store_true")
        debug_group.add_argument("--no-debug", help="Turn off debug", action="store_true")

        reloader_group = gui_parser.add_mutually_exclusive_group()
        reloader_group.add_argument("--use-reloader", help="Auto reload on code changes", action="store_true")
        reloader_group.add_argument("--no-reloader", help="No reload on code changes", action="store_true")

    @classmethod
    def parse_arguments(cls):
        return _CLI._parse()
