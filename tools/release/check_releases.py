import sys
import os


if __name__ == "__main__":
    _path = sys.argv[1]
    _version = sys.argv[2]

    packages = [
        f"taipy-{_version}.tar.gz",
        f"taipy-config-{_version}.tar.gz",
        f"taipy-core-{_version}.tar.gz",
        f"taipy-rest-{_version}.tar.gz",
        f"taipy-gui-{_version}.tar.gz",
        f"taipy-templates-{_version}.tar.gz",
    ]

    for package in packages:
        if not os.path.exists(os.path.join(_path, package)):
            print(f"Package {package} does not exist")
            sys.exit(1)
