# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from __future__ import annotations

from typing import Literal

from zope.interface import Interface, implementer

from twisted.python import components


def foo() -> Literal[2]:
    return 2


class X:
    def __init__(self, x: str) -> None:
        self.x = x

    def do(self) -> None:
        # print 'X',self.x,'doing!'
        pass


class XComponent(components.Componentized):
    pass


class IX(Interface):
    pass


@implementer(IX)
class XA(components.Adapter):
    def method(self) -> None:
        # Kick start :(
        pass


components.registerAdapter(XA, X, IX)
