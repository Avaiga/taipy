from taipy.core import *
import taipy.gui as gui
import taipy.rest as rest

__author__ = """Avaiga"""
__email__ = "taipy.dev@avaiga.com"


def run(page):
    from taipy.rest.run import app

    gui.Gui(flask=app).run()
