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

from ._argparse import _ArgumentParser


class _CLI:
    """Argument parser for Taipy application."""

    # The conflict_handler is set to "resolve" to override conflict arguments
    _main_parser = _ArgumentParser(conflict_handler="resolve")
    _subparser_action = _main_parser.add_subparsers()

    sub_taipyparsers: Dict[str, argparse.ArgumentParser] = {}

    @classmethod
    def _add_subparser(cls, name: str, **kwargs) -> argparse.ArgumentParser:
        """Create a new subparser and return a argparse handler."""
        if subparser := cls.sub_taipyparsers.get(name):
            return subparser

        subparser = cls._subparser_action.add_parser(
            name=name,
            conflict_handler="resolve",
            **kwargs,
        )
        cls.sub_taipyparsers[name] = subparser
        subparser.set_defaults(which=name)
        return subparser

    @classmethod
    def _parse(cls):
        """Parse and return only known arguments."""
        args, _ = cls._main_parser.parse_known_args()
        return args

    @classmethod
    def _remove_subparser(cls, name: str):
        """Remove a subparser from argparse."""
        cls.sub_taipyparsers.pop(name, None)

        cls._subparser_action._name_parser_map.pop(name, None)

        for action in cls._subparser_action._choices_actions:
            if action.dest == name:
                cls._subparser_action._choices_actions.remove(action)
