from unittest.mock import patch, MagicMock, ANY
from src.taipy.rest.app import create_app


@patch("taipy.gui.Gui")
@patch("src.taipy.rest.app.gui_installed")
def test_create_app_with_gui_installed(gui_installed: MagicMock, Gui: MagicMock):
    gui_installed.return_value = True
    app = create_app()
    Gui.assert_called_once_with(flask=app, pages=ANY)
    Gui.return_value.run.assert_called_once_with(run_server=False)


@patch("taipy.gui.Gui")
@patch("src.taipy.rest.app.gui_installed")
def test_create_app_without_gui_installed(gui_installed: MagicMock, Gui: MagicMock):
    gui_installed.return_value = False
    create_app()
    Gui.assert_not_called()
