import os
from pathlib import Path

from taipy.gui import Gui


def test_folder_pages_binding(gui: Gui):
    folder_path = f"{Path(Path(__file__).parent.resolve())}{os.path.sep}sample_assets"
    gui.add_pages(folder_path)
    gui.run(run_server=False)
    assert len(gui._config.routes) == 3  # 2 files -> 2 routes + 1 default route
    assert len(gui._config.pages) == 3  # 2 files -> 2 pages + 1 default page
    assert len(gui._flask_blueprint) == 5
