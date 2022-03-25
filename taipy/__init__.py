from taipy.core import *
import taipy.gui as gui
import taipy.rest as rest

__author__ = """Avaiga"""
__email__ = "taipy.dev@avaiga.com"


def run(gui_app: gui.Gui = None, **kwargs):
    """
    Run the REST API with the GUI if passed in parameters.

    Parameters:
        gui (Optional[`Gui^`]): Gui application to run. Only REST API will be running if it is not provided.
        **kwargs: Other parameters to provide to the Flask server.
    """
    if isinstance(gui_app, gui.Gui):
        from taipy.rest.run import app
        gui_app.bind_flask(app)
        gui_app.run(**kwargs)
    else:
        rest.run(**kwargs)