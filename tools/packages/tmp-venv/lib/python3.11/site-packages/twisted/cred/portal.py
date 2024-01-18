# -*- test-case-name: twisted.cred.test.test_cred -*-

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
The point of integration of application and authentication.
"""


from typing import Callable, Dict, Iterable, List, Tuple, Type, Union

from zope.interface import Interface, providedBy

from twisted.cred import error
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import ICredentials
from twisted.internet import defer
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.python import failure, reflect

# To say 'we need an Interface object', we have to say Type[Interface];
# although zope.interface has no type/instance distinctions within the
# implementation of Interface itself (subclassing it actually instantiates it),
# since mypy-zope treats Interface objects *as* types, this is how you have to
# treat it.
_InterfaceItself = Type[Interface]

# This is the result shape for both IRealm.requestAvatar and Portal.login,
# although the former is optionally allowed to return synchronously and the
# latter must be Deferred.
_requestResult = Tuple[_InterfaceItself, object, Callable[[], None]]


class IRealm(Interface):
    """
    The realm connects application-specific objects to the
    authentication system.
    """

    def requestAvatar(
        avatarId: Union[bytes, Tuple[()]], mind: object, *interfaces: _InterfaceItself
    ) -> Union[Deferred[_requestResult], _requestResult]:
        """
        Return avatar which provides one of the given interfaces.

        @param avatarId: a string that identifies an avatar, as returned by
            L{ICredentialsChecker.requestAvatarId<twisted.cred.checkers.ICredentialsChecker.requestAvatarId>}
            (via a Deferred).  Alternatively, it may be
            C{twisted.cred.checkers.ANONYMOUS}.
        @param mind: usually None.  See the description of mind in
            L{Portal.login}.
        @param interfaces: the interface(s) the returned avatar should
            implement, e.g.  C{IMailAccount}.  See the description of
            L{Portal.login}.

        @returns: a deferred which will fire a tuple of (interface,
            avatarAspect, logout), or the tuple itself.  The interface will be
            one of the interfaces passed in the 'interfaces' argument.  The
            'avatarAspect' will implement that interface.  The 'logout' object
            is a callable which will detach the mind from the avatar.
        """


class Portal:
    """
    A mediator between clients and a realm.

    A portal is associated with one Realm and zero or more credentials checkers.
    When a login is attempted, the portal finds the appropriate credentials
    checker for the credentials given, invokes it, and if the credentials are
    valid, retrieves the appropriate avatar from the Realm.

    This class is not intended to be subclassed.  Customization should be done
    in the realm object and in the credentials checker objects.
    """

    checkers: Dict[Type[Interface], ICredentialsChecker]

    def __init__(
        self, realm: IRealm, checkers: Iterable[ICredentialsChecker] = ()
    ) -> None:
        """
        Create a Portal to a L{IRealm}.
        """
        self.realm = realm
        self.checkers = {}
        for checker in checkers:
            self.registerChecker(checker)

    def listCredentialsInterfaces(self) -> List[Type[Interface]]:
        """
        Return list of credentials interfaces that can be used to login.
        """
        return list(self.checkers.keys())

    def registerChecker(
        self, checker: ICredentialsChecker, *credentialInterfaces: Type[Interface]
    ) -> None:
        if not credentialInterfaces:
            credentialInterfaces = checker.credentialInterfaces
        for credentialInterface in credentialInterfaces:
            self.checkers[credentialInterface] = checker

    def login(
        self, credentials: ICredentials, mind: object, *interfaces: Type[Interface]
    ) -> Deferred[_requestResult]:
        """
        @param credentials: an implementor of
            L{twisted.cred.credentials.ICredentials}

        @param mind: an object which implements a client-side interface for
            your particular realm.  In many cases, this may be None, so if the
            word 'mind' confuses you, just ignore it.

        @param interfaces: list of interfaces for the perspective that the mind
            wishes to attach to. Usually, this will be only one interface, for
            example IMailAccount. For highly dynamic protocols, however, this
            may be a list like (IMailAccount, IUserChooser, IServiceInfo).  To
            expand: if we are speaking to the system over IMAP, any information
            that will be relayed to the user MUST be returned as an
            IMailAccount implementor; IMAP clients would not be able to
            understand anything else. Any information about unusual status
            would have to be relayed as a single mail message in an
            otherwise-empty mailbox. However, in a web-based mail system, or a
            PB-based client, the ``mind'' object inside the web server
            (implemented with a dynamic page-viewing mechanism such as a
            Twisted Web Resource) or on the user's client program may be
            intelligent enough to respond to several ``server''-side
            interfaces.

        @return: A deferred which will fire a tuple of (interface,
            avatarAspect, logout).  The interface will be one of the interfaces
            passed in the 'interfaces' argument.  The 'avatarAspect' will
            implement that interface. The 'logout' object is a callable which
            will detach the mind from the avatar. It must be called when the
            user has conceptually disconnected from the service. Although in
            some cases this will not be in connectionLost (such as in a
            web-based session), it will always be at the end of a user's
            interactive session.
        """
        for i in self.checkers:
            if i.providedBy(credentials):
                return maybeDeferred(
                    self.checkers[i].requestAvatarId, credentials
                ).addCallback(self.realm.requestAvatar, mind, *interfaces)
        ifac = providedBy(credentials)
        return defer.fail(
            failure.Failure(
                error.UnhandledCredentials(
                    "No checker for %s" % ", ".join(map(reflect.qual, ifac))
                )
            )
        )
