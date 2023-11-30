import json
import os


def _get_version():
    with open(f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}version.json") as version_file:
        version = json.load(version_file)
        version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
        if vext := version.get("ext"):
            version_string = f"{version_string}.{vext}"
    return version_string
