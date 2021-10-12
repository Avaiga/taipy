from ._md_ext import makeTaipyExtension
from .gui import Gui
from .renderers import Html, Markdown


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
