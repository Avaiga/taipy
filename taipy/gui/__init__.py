from .gui import Gui
from ._md_ext import makeTaipyExtension


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
