from ._md_ext import makeTaipyExtension
from .gui import Gui
from .renderer import Html, Markdown


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
