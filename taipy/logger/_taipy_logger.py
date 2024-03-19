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

import logging.config
import os
import sys


class _TaipyLogger:
    _ENVIRONMENT_VARIABLE_NAME_WITH_LOGGER_CONFIG_PATH = "TAIPY_LOGGER_CONFIG_PATH"

    __logger = None

    @classmethod
    def _get_logger(cls):
        cls._ENVIRONMENT_VARIABLE_NAME_WITH_LOGGER_CONFIG_PATH = "TAIPY_LOGGER_CONFIG_PATH"

        if cls.__logger:
            return cls.__logger

        if config_filename := os.environ.get(cls._ENVIRONMENT_VARIABLE_NAME_WITH_LOGGER_CONFIG_PATH):
            logging.config.fileConfig(config_filename)
            cls.__logger = logging.getLogger("Taipy")
        else:
            cls.__logger = logging.getLogger("Taipy")
            cls.__logger.setLevel(logging.INFO)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.INFO)
            f = logging.Formatter("[%(asctime)s.%(msecs)03d][%(name)s][%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
            ch.setFormatter(f)
            cls.__logger.addHandler(ch)
        return cls.__logger
