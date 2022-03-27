from taipy.gui import Gui
from taipy.rest import Rest


def _run(gui: Gui = None, rest: Rest = None, **kwargs):
    """
        Run the REST API with the GUI if passed in parameters.

        Parameters:
            gui (Optional[`Gui^`]): Gui application to run.
            rest (Optional[`Rest^`]): Rest application to run.
            **kwargs: Other parameters to provide to the Flask server.
        """
    if gui and rest:
        gui._set_flask(rest._app)
        gui.run(**kwargs)
    else:
        app = rest or gui
        app.run(**kwargs)
