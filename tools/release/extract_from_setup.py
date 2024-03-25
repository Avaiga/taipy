import sys


def extract_gui_version(base_path: str) -> None:
    with open("setup.py") as f:
        for line in f:
            if "taipy-gui" in line:
                start = line.find("taipy-gui")
                end = line.rstrip().find('",')
                print(f"VERSION={line[start:end]}")  # noqa: T201
                break


if __name__ == "__main__":
    extract_gui_version(sys.argv[1])
