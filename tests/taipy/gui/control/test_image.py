import os
import pathlib
from importlib import util

from taipy.gui import Gui


def test_image_url_md(gui: Gui, helpers):
    gui._bind_var_val("content", "some_url")
    md_string = "<|{content}|image|>"
    expected_list = [
        "<Image",
        "content={_TpCi_content}",
        'defaultContent="some_url"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_image_file_md(gui: Gui, helpers):
    with open((pathlib.Path(__file__).parent.parent / "resources" / "fred.png").resolve(), "rb") as content:
        gui._bind_var_val("content", content.read())
        md_string = "<|{content}|image|>"
        expected_list = [
            "<Image",
            'defaultContent="data:image/png;base64,',
        ]
        if not util.find_spec("magic"):
            expected_list = ["<Image", 'defaultContent="/taipy-content/taipyStatic0/TaiPyContent.', ".bin"]
        helpers.test_control_md(gui, md_string, expected_list)


def test_image_path_md(gui: Gui, helpers):
    gui._bind_var_val("content", str((pathlib.Path(__file__).parent.parent / "resources" / "fred.png").resolve()))
    md_string = "<|{content}|image|>"
    expected_list = [
        "<Image",
        'defaultContent="/taipy-content/taipyStatic0/fred.png',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_image_bad_file_md(gui: Gui, helpers):
    with open(os.path.abspath(__file__), "rb") as content:
        gui._bind_var_val("content", content.read())
        md_string = "<|{content}|image|>"
        expected_list = [
            "<Image",
            'defaultContent="Invalid content: text/x',
        ]
        if not util.find_spec("magic"):
            expected_list = ["<Image", 'defaultContent="/taipy-content/taipyStatic0/TaiPyContent.', ".bin"]
        helpers.test_control_md(gui, md_string, expected_list)


def test_image_url_html(gui: Gui, helpers):
    gui._bind_var_val("content", "some_url")
    html_string = '<taipy:image content="{content}" on_action="action" />'
    expected_list = [
        "<Image",
        'defaultContent="some_url"',
        'tp_onAction="action"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
