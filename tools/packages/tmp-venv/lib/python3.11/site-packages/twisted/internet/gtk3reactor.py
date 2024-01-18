# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module is a legacy compatibility alias for L{twisted.internet.gireactor}.
See that module instead.
"""

from incremental import Version

from ._deprecate import deprecatedGnomeReactor

deprecatedGnomeReactor("gtk3reactor", Version("Twisted", 23, 8, 0))

from twisted.internet import gireactor

Gtk3Reactor = gireactor.GIReactor
PortableGtk3Reactor = gireactor.PortableGIReactor

install = gireactor.install

__all__ = ["install"]
