from taipy.gui import Gui
from pathlib import Path
import os


def test_folder_pages_binding(gui: Gui):
    folder_path = f"{Path(Path(__file__).parent.resolve())}{os.path.sep}sample_assets"
    gui.add_pages(folder_path)
    gui.run(run_server=False)
    assert len(gui._config.routes) == 2
    assert len(gui._config.pages) == 2
    assert len(gui._flask_blueprint) == 1
