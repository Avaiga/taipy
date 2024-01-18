"""
Support similar deprecation of several reactors.
"""

import warnings

from incremental import Version, getVersionString

from twisted.python.deprecate import DEPRECATION_WARNING_FORMAT


def deprecatedGnomeReactor(name: str, version: Version) -> None:
    """
    Emit a deprecation warning about a gnome-related reactor.

    @param name: The name of the reactor.  For example, C{"gtk2reactor"}.

    @param version: The version in which the deprecation was introduced.
    """
    stem = DEPRECATION_WARNING_FORMAT % {
        "fqpn": "twisted.internet." + name,
        "version": getVersionString(version),
    }
    msg = stem + ".  Please use twisted.internet.gireactor instead."
    warnings.warn(msg, category=DeprecationWarning)
