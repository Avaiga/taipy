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

import sys

from cookiecutter.main import cookiecutter

from taipy.config._cli._cli import _CLI


class _ScaffoldCLI:
    __TEMPLATE_MAP = {
        "default": "default_template_path",
    }

    @classmethod
    def create_parser(cls):
        create_parser = _CLI._add_subparser("create", help="Create a new Taipy application.")
        create_parser.add_argument(
            "--template",
            choices=["default"],
            default="default",
            help="The Taipy template to create new application.",
        )

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()

        if getattr(args, "which", None) == "create":
            cookiecutter(cls.__TEMPLATE_MAP[args.template])
            sys.exit(0)
