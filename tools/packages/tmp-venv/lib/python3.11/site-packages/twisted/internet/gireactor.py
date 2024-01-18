# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module provides support for Twisted to interact with the glib
mainloop via GObject Introspection.

In order to use this support, simply do the following::

    from twisted.internet import gireactor
    gireactor.install()

If you wish to use a GApplication, register it with the reactor::

    from twisted.internet import reactor
    reactor.registerGApplication(app)

Then use twisted.internet APIs as usual.

On Python 3, pygobject v3.4 or later is required.
"""


from typing import Union

from gi.repository import GLib  # type:ignore[import]

from twisted.internet import _glibbase
from twisted.internet.error import ReactorAlreadyRunning
from twisted.python import runtime

if getattr(GLib, "threads_init", None) is not None:
    GLib.threads_init()


class GIReactor(_glibbase.GlibReactorBase):
    """
    GObject-introspection event loop reactor.

    @ivar _gapplication: A C{Gio.Application} instance that was registered
        with C{registerGApplication}.
    """

    # By default no Application is registered:
    _gapplication = None

    def __init__(self, useGtk=False):
        _glibbase.GlibReactorBase.__init__(self, GLib, None)

    def registerGApplication(self, app):
        """
        Register a C{Gio.Application} or C{Gtk.Application}, whose main loop
        will be used instead of the default one.

        We will C{hold} the application so it doesn't exit on its own. In
        versions of C{python-gi} 3.2 and later, we exit the event loop using
        the C{app.quit} method which overrides any holds. Older versions are
        not supported.
        """
        if self._gapplication is not None:
            raise RuntimeError("Can't register more than one application instance.")
        if self._started:
            raise ReactorAlreadyRunning(
                "Can't register application after reactor was started."
            )
        if not hasattr(app, "quit"):
            raise RuntimeError(
                "Application registration is not supported in"
                " versions of PyGObject prior to 3.2."
            )
        self._gapplication = app

        def run():
            app.hold()
            app.run(None)

        self._run = run

        self._crash = app.quit


class PortableGIReactor(_glibbase.GlibReactorBase):
    """
    Portable GObject Introspection event loop reactor.
    """

    def __init__(self, useGtk=False):
        super().__init__(GLib, None, useGtk=useGtk)

    def registerGApplication(self, app):
        """
        Register a C{Gio.Application} or C{Gtk.Application}, whose main loop
        will be used instead of the default one.
        """
        raise NotImplementedError("GApplication is not currently supported on Windows.")

    def simulate(self) -> None:
        """
        For compatibility only. Do nothing.
        """


def install(useGtk: bool = False) -> Union[GIReactor, PortableGIReactor]:
    """
    Configure the twisted mainloop to be run inside the glib mainloop.

    @param useGtk: A hint that the Gtk GUI will or will not be used.  Currently
        does not modify any behavior.
    """
    reactor: Union[GIReactor, PortableGIReactor]
    if runtime.platform.getType() == "posix":
        reactor = GIReactor(useGtk=useGtk)
    else:
        reactor = PortableGIReactor(useGtk=useGtk)

    from twisted.internet.main import installReactor

    installReactor(reactor)
    return reactor


__all__ = ["install"]
