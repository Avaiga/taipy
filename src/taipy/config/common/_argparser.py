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

import argparse
from typing import Dict


class _Argparser:
    """Argument parser for Taipy application."""

    # The conflict_handler is set to "resolve" to override conflict arguments
    parser = argparse.ArgumentParser(conflict_handler="resolve")

    arg_groups: Dict[str, argparse._ArgumentGroup] = {}

    @classmethod
    def _add_groupparser(cls, title: str, description: str = "") -> argparse._ArgumentGroup:
        """Create a new group for arguments and return a argparser handle."""

        try:
            return cls.arg_groups[title]
        except KeyError:
            arg_group = cls.parser.add_argument_group(title=title, description=description)
            cls.arg_groups[title] = arg_group
            return arg_group

    @classmethod
    def _parse(cls):
        """Parse and return only known arguments."""
        args, _ = cls.parser.parse_known_args()
        return args
