import os
import sys
from pathlib import Path


def build_gui(root_path):
    print(f"Building taipy-gui frontend bundle in {root_path}.")
    already_exists = (root_path / "taipy" / "gui" / "webapp" / "index.html").exists()
    if already_exists:
        print(f'Found taipy-gui frontend bundle in {root_path  / "taipy" / "gui" / "webapp"}.')
    else:
        os.system("cd frontend/taipy-gui/dom && npm ci")
        os.system("cd frontend/taipy-gui && npm ci --omit=optional && npm run build")


def build_taipy(root_path):
    print(f"Building taipy frontend bundle in {root_path}.")
    already_exists = (root_path / "taipy" / "gui_core" / "lib" / "taipy-gui-core.js").exists()
    if already_exists:
        print(f'Found taipy frontend bundle in {root_path / "taipy" / "gui_core" / "lib"}.')
    else:
        # Specify the correct path to taipy-gui in gui/.env file
        env_file_path = root_path / "frontend" / "taipy" / ".env"
        if not os.path.exists(env_file_path):
            with open(env_file_path, "w") as env_file:
                env_file.write(f"TAIPY_GUI_DIR={root_path}\n")
        os.system("cd frontend/taipy && npm ci && npm run build")


if __name__ == "__main__":
    root_path = Path(__file__).absolute().parent.parent.parent
    if len(sys.argv) > 1:
        if sys.argv[1] == "gui":
            build_gui(root_path)
        elif sys.argv[1] == "taipy":
            build_taipy(root_path)
    else:
        build_gui(root_path)
        build_taipy(root_path)
