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

import argparse
from typing import Dict


class _CLI:
    """Argument parser for Taipy application."""

    # The conflict_handler is set to "resolve" to override conflict arguments
    _subparser_action = None
    _parser = argparse.ArgumentParser(conflict_handler="resolve")

    _sub_taipyparsers: Dict[str, argparse.ArgumentParser] = {}
    _arg_groups: Dict[str, argparse._ArgumentGroup] = {}

    @classmethod
    def _add_subparser(cls, name: str, **kwargs) -> argparse.ArgumentParser:
        """Create a new subparser and return a argparse handler."""
        if subparser := cls._sub_taipyparsers.get(name):
            return subparser

        if not cls._subparser_action:
            cls._subparser_action = cls._parser.add_subparsers()

        subparser = cls._subparser_action.add_parser(
            name=name,
            conflict_handler="resolve",
            **kwargs,
        )
        cls._sub_taipyparsers[name] = subparser
        subparser.set_defaults(which=name)
        return subparser

    @classmethod
    def _add_groupparser(cls, title: str, description: str = "") -> argparse._ArgumentGroup:
        """Create a new group for arguments and return a argparser handler."""
        if groupparser := cls._arg_groups.get(title):
            return groupparser

        groupparser = cls._parser.add_argument_group(title=title, description=description)
        cls._arg_groups[title] = groupparser
        return groupparser

    @classmethod
    def _parse(cls):
        """Parse and return only known arguments."""
        args, _ = cls._parser.parse_known_args()
        return args

    @classmethod
    def _remove_argument(cls, arg: str):
        """Remove an argument from the parser. Note that the `arg` must be without --.

        Source: https://stackoverflow.com/questions/32807319/disable-remove-argument-in-argparse
        """
        for action in cls._parser._actions:
            opts = action.option_strings
            if (opts and opts[0] == arg) or action.dest == arg:
                cls._parser._remove_action(action)
                break

        for argument_group in cls._parser._action_groups:
            for group_action in argument_group._group_actions:
                opts = group_action.option_strings
                if (opts and opts[0] == arg) or group_action.dest == arg:
                    argument_group._group_actions.remove(group_action)
                    return
