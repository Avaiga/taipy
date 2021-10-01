from ._md_ext import makeTaipyExtension
from .gui import Gui


def makeExtension(*args, **kwargs):
    return makeTaipyExtension(*args, **kwargs)
