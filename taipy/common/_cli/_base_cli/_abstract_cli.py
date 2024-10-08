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

import sys
from abc import abstractmethod
from difflib import SequenceMatcher
from typing import List, Optional

from taipy.common.logger._taipy_logger import _TaipyLogger

from ._taipy_parser import _TaipyParser


class _AbstractCLI:
    _logger = _TaipyLogger._get_logger()

    _COMMAND_NAME: Optional[str] = None
    _ARGUMENTS: List[str] = []
    SIMILARITY_THRESHOLD = 0.8

    @classmethod
    @abstractmethod
    def create_parser(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def handle_command(cls):
        raise NotImplementedError

    @classmethod
    def _parse_arguments(cls):
        arguments, unknown_arguments = _TaipyParser._parser.parse_known_arguments()

        if getattr(arguments, "which", None) != cls._COMMAND_NAME:
            return

        if unknown_arguments:
            _TaipyParser._sub_taipyparsers.get(cls._COMMAND_NAME).print_help()
            for unknown_arg in unknown_arguments:
                if not unknown_arg.startswith("-"):
                    continue

                error_message = f"Unknown arguments: {unknown_arg}."
                similar_arguments = [
                    arg
                    for arg in cls._ARGUMENTS
                    if SequenceMatcher(None, unknown_arg, arg).ratio() > cls.SIMILARITY_THRESHOLD
                ]
                if similar_arguments:
                    error_message += f" Did you mean: {' or '.join(similar_arguments)}?"
                cls._logger.error(error_message)
            cls._logger.error("Please refer to the help message above for more information.")
            sys.exit(1)

        return arguments
