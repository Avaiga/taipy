from typing import Dict

import toml  # type: ignore


class TomlSerializer:
    """
    Transform configuration from the TOML representation to Python Dict
    """

    @staticmethod
    def read(filename: str) -> Dict:
        return dict(toml.load(filename))

    @staticmethod
    def write(configuration: Dict, filename: str):
        with open(filename, "w") as fd:
            toml.dump(configuration, fd)
