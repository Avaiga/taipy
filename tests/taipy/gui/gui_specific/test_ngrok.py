import time
from importlib import util
from urllib.request import urlopen

from taipy.gui import Gui


def test_ngrok(gui: Gui, helpers, ngrok):
    if util.find_spec("pyngrok") and util.find_spec("pytest_ngrok"):
        gui.add_page("test", "# hi")
        gui.run(run_in_thread=True)
        while not helpers.port_check():
            time.sleep(0.1)
        remote_url = ngrok(gui._get_app_config("port", 5000))
        assert ">hi</h1>" in urlopen(f"{remote_url}/taipy-jsx/test/").read().decode("utf-8")
