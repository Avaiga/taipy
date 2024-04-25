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

import pathlib
import sys

from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

import taipy

from ._base_cli._abstract_cli import _AbstractCLI
from ._base_cli._taipy_parser import _TaipyParser


class _ScaffoldCLI(_AbstractCLI):
    __TAIPY_PATH = pathlib.Path(taipy.__file__).parent.resolve() / "templates"
    _TEMPLATE_MAP = {str(x.name): str(x) for x in __TAIPY_PATH.iterdir() if x.is_dir() and not x.name.startswith("_")}

    _COMMAND_NAME = "create"
    _ARGUMENTS = ["--template"]

    @classmethod
    def create_parser(cls):
        create_parser = _TaipyParser._add_subparser(
            cls._COMMAND_NAME,
            help="Create a new Taipy application using pre-defined templates.",
        )
        create_parser.add_argument(
            "--template",
            choices=list(cls._TEMPLATE_MAP.keys()),
            default="default",
            help="The Taipy template to create new application.",
        )

    @classmethod
    def handle_command(cls):
        args = cls._parse_arguments()
        if not args:
            return
        try:
            cookiecutter(cls._TEMPLATE_MAP[args.template])
        except OutputDirExistsException as err:
           error_msg = f"{str(err)}. Please remove the existing directory or provide a new folder name."
           print(error_msg)
            sys.exit(1)
        sys.exit(0)
