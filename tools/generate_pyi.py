import os

os.system('pipenv run stubgen ./src/taipy/gui/gui.py --no-import --parse-only --include-private --export-less -o ./')

from src.taipy.gui.config import Config

gui_config = "".join(
    f", {k}: {v.__name__} = ..." if "<class" in str(v) else f", {k}: {str(v).replace('typing', 't').replace('src.taipy.gui.config.', '')} = ..."
    for k, v in Config.__annotations__.items()
)

replaced_content = ""
with open("./src/taipy/gui/gui.pyi", "r") as file:
    for line in file:
        if "def run(" in line:
            line = line.replace(", run_server: bool = ..., run_in_thread: bool = ..., async_mode: str = ..., **kwargs", gui_config)
        replaced_content = replaced_content + line

with open("./src/taipy/gui/gui.pyi", "w") as write_file:
    write_file.write(replaced_content)

os.system("pipenv run isort src/taipy/gui/gui.pyi")
os.system("pipenv run black src/taipy/gui/gui.pyi")
