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

import pathlib
import sys

from cookiecutter.main import cookiecutter

import taipy
from taipy._cli._base_cli import _CLI


class _ScaffoldCLI:
    __TAIPY_PATH = pathlib.Path(taipy.__file__).parent.resolve() / "templates"

    _TEMPLATE_MAP = {str(x.name): str(x) for x in __TAIPY_PATH.iterdir() if x.is_dir()}

    @classmethod
    def create_parser(cls):
        create_parser = _CLI._add_subparser("create", help="Create a new Taipy application.")
        create_parser.add_argument(
            "--template",
            choices=list(cls._TEMPLATE_MAP.keys()),
            default="default",
            help="The Taipy template to create new application.",
        )

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()

        if getattr(args, "which", None) == "create":
            cookiecutter(cls._TEMPLATE_MAP[args.template])
            sys.exit(0)
