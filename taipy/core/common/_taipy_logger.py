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
            formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
            ch.setFormatter(formatter)
            cls.__logger.addHandler(ch)
        return cls.__logger
