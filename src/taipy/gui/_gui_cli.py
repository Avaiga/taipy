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

from typing import Dict, Tuple

from taipy._cli._base_cli import _CLI


class _GuiCLI:
    """Command-line interface of GUI."""

    __GUI_ARGS: Dict[Tuple, Dict] = {
        ("--port", "-P"): {
            "dest": "taipy_port",
            "metavar": "PORT",
            "nargs": "?",
            "default": "",
            "const": "",
            "help": "Specify server port",
        },
        ("--host", "-H"): {
            "dest": "taipy_host",
            "metavar": "HOST",
            "nargs": "?",
            "default": "",
            "const": "",
            "help": "Specify server host",
        },
        ("--ngrok-token",): {
            "dest": "taipy_ngrok_token",
            "metavar": "NGROK_TOKEN",
            "nargs": "?",
            "default": "",
            "const": "",
            "help": "Specify NGROK Authtoken",
        },
        ("--webapp-path",): {
            "dest": "taipy_webapp_path",
            "metavar": "WEBAPP_PATH",
            "nargs": "?",
            "default": "",
            "const": "",
            "help": "The path to the web app to be used. The default is the webapp directory under gui in the Taipy GUI package directory.",
        },
    }

    __DEBUG_ARGS: Dict[str, Dict] = {
        "--debug": {"dest": "taipy_debug", "help": "Turn on debug", "action": "store_true"},
        "--no-debug": {"dest": "taipy_no_debug", "help": "Turn off debug", "action": "store_true"},
    }

    __RELOADER_ARGS: Dict[str, Dict] = {
        "--use-reloader": {"dest": "taipy_use_reloader", "help": "Auto reload on code changes", "action": "store_true"},
        "--no-reloader": {"dest": "taipy_no_reloader", "help": "No reload on code changes", "action": "store_true"},
    }

    @classmethod
    def create_parser(cls):
        gui_parser = _CLI._add_groupparser("Taipy GUI", "Optional arguments for Taipy GUI service")

        for args, arg_dict in cls.__GUI_ARGS.items():
            taipy_arg = (args[0], cls.__add_taipy_prefix(args[0]), *args[1:])
            gui_parser.add_argument(*taipy_arg, **arg_dict)

        debug_group = gui_parser.add_mutually_exclusive_group()
        for debug_arg, debug_arg_dict in cls.__DEBUG_ARGS.items():
            debug_group.add_argument(debug_arg, cls.__add_taipy_prefix(debug_arg), **debug_arg_dict)

        reloader_group = gui_parser.add_mutually_exclusive_group()
        for reloader_arg, reloader_arg_dict in cls.__RELOADER_ARGS.items():
            reloader_group.add_argument(reloader_arg, cls.__add_taipy_prefix(reloader_arg), **reloader_arg_dict)

    @classmethod
    def create_run_parser(cls):
        run_parser = _CLI._add_subparser("run", help="Run a Taipy application.")
        for args, arg_dict in cls.__GUI_ARGS.items():
            run_parser.add_argument(*args, **arg_dict)

        debug_group = run_parser.add_mutually_exclusive_group()
        for debug_arg, debug_arg_dict in cls.__DEBUG_ARGS.items():
            debug_group.add_argument(debug_arg, **debug_arg_dict)

        reloader_group = run_parser.add_mutually_exclusive_group()
        for reloader_arg, reloader_arg_dict in cls.__RELOADER_ARGS.items():
            reloader_group.add_argument(reloader_arg, **reloader_arg_dict)

    @classmethod
    def parse_arguments(cls):
        return _CLI._parse()

    @classmethod
    def __add_taipy_prefix(cls, key: str):
        if key.startswith("--no-"):
            return key[:5] + "taipy-" + key[5:]

        return key[:2] + "taipy-" + key[2:]
