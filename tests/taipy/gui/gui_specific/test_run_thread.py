import time
from urllib.request import urlopen

from taipy.gui import Gui


def test_run_thread(gui: Gui, helpers):
    gui.add_page("page1", "# first page")
    gui.run(run_in_thread=True)
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">first page</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1/").read().decode("utf-8")
    gui.stop()
    while helpers.port_check():
        time.sleep(0.1)
    gui.run(run_in_thread=True)
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">first page</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1/").read().decode("utf-8")
