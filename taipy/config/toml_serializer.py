import logging
from typing import Dict

import toml  # type: ignore

from taipy.exceptions.configuration import LoadingError


class TomlSerializer:
    """
    Transform configuration from the TOML representation to Python Dict
    """

    @classmethod
    def read(cls, filename: str) -> Dict:
        try:
            return dict(toml.load(filename))
        except toml.TomlDecodeError as e:
            error_msg = f"Can not load configuration {e}"
            logging.error(error_msg)
            raise LoadingError(error_msg)

    @staticmethod
    def write(configuration: Dict, filename: str):
        with open(filename, "w") as fd:
            toml.dump(configuration, fd)
