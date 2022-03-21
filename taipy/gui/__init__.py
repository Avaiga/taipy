"""# `gui` package: Graphical User Interface


The Graphical User Interface module of Taipy lets you
run a Web server that a Web browser can connect to.

The server generates Web pages on the fly, configured by
the application developer.

Each page can contain regular text and images, as well
as Taipy controls that are typically linked to some
value that is managed by the whole Taipy application.
"""

from .gui import Gui
from .gui_actions import download, hold_control, navigate, notify, resume_control
from .icon import Icon
from .renderers import Html, Markdown
from .state import State
