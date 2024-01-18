# -*- test-case-name: twisted.test.test_paths -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Object-oriented filesystem path representation.
"""

from __future__ import annotations

import base64
import errno
import os
import sys
from os import listdir, stat, utime
from os.path import (
    abspath,
    basename,
    dirname,
    exists,
    isabs,
    islink,
    join as joinpath,
    normpath,
    splitext,
)
from stat import (
    S_IMODE,
    S_IRGRP,
    S_IROTH,
    S_IRUSR,
    S_ISBLK,
    S_ISDIR,
    S_ISREG,
    S_ISSOCK,
    S_IWGRP,
    S_IWOTH,
    S_IWUSR,
    S_IXGRP,
    S_IXOTH,
    S_IXUSR,
)
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    AnyStr,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

from zope.interface import Attribute, Interface, implementer

from typing_extensions import Literal

from twisted.python.compat import cmp, comparable
from twisted.python.runtime import platform
from twisted.python.util import FancyEqMixin
from twisted.python.win32 import (
    ERROR_DIRECTORY,
    ERROR_FILE_NOT_FOUND,
    ERROR_INVALID_NAME,
    ERROR_PATH_NOT_FOUND,
    O_BINARY,
)

# Please keep this as light as possible on other Twisted imports; many, many
# things import this module, and it would be good if it could easily be
# modified for inclusion in the standard library.  --glyph


_CREATE_FLAGS = os.O_EXCL | os.O_CREAT | os.O_RDWR | O_BINARY
_Self = TypeVar("_Self", bound="AbstractFilePath[Any]")


randomBytes = os.urandom
armor = base64.urlsafe_b64encode


class IFilePath(Interface):
    """
    File path object.

    A file path represents a location for a file-like-object and can be
    organized into a hierarchy; a file path can can children which are
    themselves file paths.

    A file path has a name which unique identifies it in the context of its
    parent (if it has one); a file path can not have two children with the same
    name.  This name is referred to as the file path's "base name".

    A series of such names can be used to locate nested children of a file
    path; such a series is referred to as the child's "path", relative to the
    parent.  In this case, each name in the path is referred to as a "path
    segment"; the child's base name is the segment in the path.

    When representing a file path as a string, a "path separator" is used to
    delimit the path segments within the string.  For a file system path, that
    would be C{os.sep}.

    Note that the values of child names may be restricted.  For example, a file
    system path will not allow the use of the path separator in a name, and
    certain names (e.g. C{"."} and C{".."}) may be reserved or have special
    meanings.

    @since: 12.1
    """

    sep = Attribute("The path separator to use in string representations")

    def child(name: AnyStr) -> IFilePath:
        """
        Obtain a direct child of this file path.  The child may or may not
        exist.

        @param name: the name of a child of this path. C{name} must be a direct
            child of this path and may not contain a path separator.
        @return: the child of this path with the given C{name}.
        @raise InsecurePath: if C{name} describes a file path that is not a
            direct child of this file path.
        """

    def open(mode: FileMode = "r") -> IO[bytes]:
        """
        Opens this file path with the given mode.

        @return: a file-like object.
        @raise Exception: if this file path cannot be opened.
        """

    def changed() -> None:
        """
        Clear any cached information about the state of this path on disk.
        """

    def getsize() -> int:
        """
        Retrieve the size of this file in bytes.

        @return: the size of the file at this file path in bytes.
        @raise Exception: if the size cannot be obtained.
        """

    def getModificationTime() -> float:
        """
        Retrieve the time of last access from this file.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """

    def getStatusChangeTime() -> float:
        """
        Retrieve the time of the last status change for this file.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """

    def getAccessTime() -> float:
        """
        Retrieve the time that this file was last accessed.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """

    def exists() -> bool:
        """
        Check if this file path exists.

        @return: C{True} if the file at this file path exists, C{False}
            otherwise.
        @rtype: L{bool}
        """

    def isdir() -> bool:
        """
        Check if this file path refers to a directory.

        @return: C{True} if the file at this file path is a directory, C{False}
            otherwise.
        """

    def isfile() -> bool:
        """
        Check if this file path refers to a regular file.

        @return: C{True} if the file at this file path is a regular file,
            C{False} otherwise.
        """

    def children() -> Iterable[IFilePath]:
        """
        List the children of this path object.

        @return: a sequence of the children of the directory at this file path.
        @raise Exception: if the file at this file path is not a directory.
        """

    def basename() -> Union[str, bytes]:
        """
        Retrieve the final component of the file path's path (everything after
        the final path separator).

        @note: In implementors, the return type should be generic, i.e.
            C{AbstractFilePath[str].basename()} is a C{str}.  However,
            L{Interface} objects cannot be generic as of this writing.

        @return: the base name of this file path.
        """

    def parent() -> IFilePath:
        """
        A file path for the directory containing the file at this file path.
        """

    def sibling(name: AnyStr) -> IFilePath:
        """
        A file path for the directory containing the file at this file path.

        @param name: the name of a sibling of this path.  C{name} must be a
            direct sibling of this path and may not contain a path separator.

        @return: a sibling file path of this one.
        """


class InsecurePath(Exception):
    """
    Error that is raised when the path provided to L{FilePath} is invalid.
    """


class LinkError(Exception):
    """
    An error with symlinks - either that there are cyclical symlinks or that
    symlink are not supported on this platform.
    """


class UnlistableError(OSError):
    """
    An exception which is used to distinguish between errors which mean 'this
    is not a directory you can list' and other, more catastrophic errors.

    This error will try to look as much like the original error as possible,
    while still being catchable as an independent type.

    @ivar originalException: the actual original exception instance.
    """

    def __init__(self, originalException: OSError):
        """
        Create an UnlistableError exception.

        @param originalException: an instance of OSError.
        """
        self.__dict__.update(originalException.__dict__)
        self.originalException = originalException


def _secureEnoughString(path: AnyStr) -> AnyStr:
    """
    Compute a string usable as a new, temporary filename.

    @param path: The path that the new temporary filename should be able to be
        concatenated with.

    @return: A pseudorandom, 16 byte string for use in secure filenames.
    @rtype: the type of C{path}
    """
    secureishString = armor(randomBytes(16))[:16]
    return _coerceToFilesystemEncoding(path, secureishString)


OtherAnyStr = TypeVar("OtherAnyStr", str, bytes)
FileMode = Literal["r", "w", "a", "r+", "w+", "a+"]


class AbstractFilePath(Generic[AnyStr]):
    """
    Abstract implementation of an L{IFilePath}; must be completed by a
    subclass.

    This class primarily exists to provide common implementations of certain
    methods in L{IFilePath}. It is *not* a required parent class for
    L{IFilePath} implementations, just a useful starting point.

    @ivar path: Subclasses must set this variable.
    """

    Selfish = TypeVar("Selfish", bound="AbstractFilePath[AnyStr]")

    path: AnyStr

    def getAccessTime(self) -> float:
        """
        Subclasses must implement this.

        @see: L{FilePath.getAccessTime}
        """
        raise NotImplementedError()

    def getModificationTime(self) -> float:
        """
        Subclasses must implement this.

        @see: L{FilePath.getModificationTime}
        """
        raise NotImplementedError()

    def getStatusChangeTime(self) -> float:
        """
        Subclasses must implement this.

        @see: L{FilePath.getStatusChangeTime}
        """
        raise NotImplementedError()

    def open(self, mode: FileMode = "r") -> IO[bytes]:
        """
        Subclasses must implement this.
        """
        raise NotImplementedError()

    def isdir(self) -> bool:
        """
        Subclasses must implement this.
        """
        raise NotImplementedError()

    def basename(self) -> AnyStr:
        """
        Subclasses must implement this.
        """
        raise NotImplementedError()

    def parent(self) -> AbstractFilePath[AnyStr]:
        """
        Subclasses must implement this.
        """
        raise NotImplementedError()

    def listdir(self) -> List[AnyStr]:
        """
        Subclasses must implement this.
        """
        raise NotImplementedError()

    def child(self, path: OtherAnyStr) -> AbstractFilePath[OtherAnyStr]:
        """
        Subclasses must implement this.
        """
        raise NotImplementedError()

    def getContent(self) -> bytes:
        """
        Retrieve the contents of the file at this path.

        @return: the contents of the file
        @rtype: L{bytes}
        """
        with self.open() as fp:
            return fp.read()

    def parents(self) -> Iterable[AbstractFilePath[AnyStr]]:
        """
        Retrieve an iterator of all the ancestors of this path.

        @return: an iterator of all the ancestors of this path, from the most
        recent (its immediate parent) to the root of its filesystem.
        """
        path = self
        parent = path.parent()
        # root.parent() == root, so this means "are we the root"
        while path != parent:
            yield parent
            path = parent
            parent = parent.parent()

    def children(self: _Self) -> Iterable[_Self]:
        """
        List the children of this path object.

        @raise OSError: If an error occurs while listing the directory.  If the
        error is 'serious', meaning that the operation failed due to an access
        violation, exhaustion of some kind of resource (file descriptors or
        memory), OSError or a platform-specific variant will be raised.

        @raise UnlistableError: If the inability to list the directory is due
        to this path not existing or not being a directory, the more specific
        OSError subclass L{UnlistableError} is raised instead.

        @return: an iterable of all currently-existing children of this object.
        """
        try:
            subnames: List[AnyStr] = self.listdir()
        except OSError as ose:
            # Under Python 3.3 and higher on Windows, WindowsError is an
            # alias for OSError.  OSError has a winerror attribute and an
            # errno attribute.
            #
            # The winerror attribute is bound to the Windows error code while
            # the errno attribute is bound to a translation of that code to a
            # perhaps equivalent POSIX error number.
            #
            # For further details, refer to:
            # https://docs.python.org/3/library/exceptions.html#OSError
            if getattr(ose, "winerror", None) in (
                ERROR_PATH_NOT_FOUND,
                ERROR_FILE_NOT_FOUND,
                ERROR_INVALID_NAME,
                ERROR_DIRECTORY,
            ):
                raise UnlistableError(ose)
            if ose.errno in (errno.ENOENT, errno.ENOTDIR):
                raise UnlistableError(ose)
            # Other possible errors here, according to linux manpages:
            # EACCES, EMIFLE, ENFILE, ENOMEM.  None of these seem like the
            # sort of thing which should be handled normally. -glyph
            raise
        result = []
        for name in subnames:
            # It's not possible to tell mypy that child/clone etc must be
            # overridden to return respecializable forms of _Self, but they
            # must, so we will say that they are.
            child: _Self = self.child(name)  # type:ignore[assignment]
            result.append(child)
        return result

    def walk(
        self: _Self,
        descend: Optional[Callable[[_Self], bool]] = None,
    ) -> Iterable[_Self]:
        """
        Yield myself, then each of my children, and each of those children's
        children in turn.

        The optional argument C{descend} is a predicate that takes a FilePath,
        and determines whether or not that FilePath is traversed/descended
        into.  It will be called with each path for which C{isdir} returns
        C{True}.  If C{descend} is not specified, all directories will be
        traversed (including symbolic links which refer to directories).

        @param descend: A one-argument callable that will return True for
            FilePaths that should be traversed, False otherwise.

        @return: a generator yielding FilePath-like objects.
        """
        yield self
        if self.isdir():
            for c in self.children():
                # we should first see if it's what we want, then we
                # can walk through the directory
                if descend is None or descend(c):
                    for subc in c.walk(descend):
                        if os.path.realpath(self.path).startswith(
                            os.path.realpath(subc.path)
                        ):
                            raise LinkError("Cycle in file graph.")
                        yield subc
                else:
                    yield c

    def sibling(self: _Self, path: OtherAnyStr) -> AbstractFilePath[OtherAnyStr]:
        """
        Return a L{FilePath} with the same directory as this instance but with
        a basename of C{path}.

        @note: for type-checking, subclasses should override this signature to
            make it clear that it returns the subclass and not
            L{AbstractFilePath}.

        @param path: The basename of the L{FilePath} to return.
        @type path: L{str}

        @return: The sibling path.
        @rtype: L{FilePath}
        """
        return self.parent().child(path)

    def descendant(
        self, segments: Sequence[OtherAnyStr]
    ) -> AbstractFilePath[OtherAnyStr]:
        """
        Retrieve a child or child's child of this path.

        @note: for type-checking, subclasses should override this signature to
            make it clear that it returns the subclass and not
            L{AbstractFilePath}.

        @param segments: A sequence of path segments as L{str} instances.

        @return: A L{FilePath} constructed by looking up the C{segments[0]}
            child of this path, the C{segments[1]} child of that path, and so
            on.

        @since: 10.2
        """
        path: AbstractFilePath[OtherAnyStr] = self  # type:ignore[assignment]
        for name in segments:
            path = path.child(name)
        return path

    def segmentsFrom(self: _Self, ancestor: _Self) -> List[AnyStr]:
        """
        Return a list of segments between a child and its ancestor.

        For example, in the case of a path X representing /a/b/c/d and a path Y
        representing /a/b, C{Y.segmentsFrom(X)} will return C{['c',
        'd']}.

        @param ancestor: an instance of the same class as self, ostensibly an
        ancestor of self.

        @raise ValueError: If the C{ancestor} parameter is not actually an
        ancestor, i.e. a path for /x/y/z is passed as an ancestor for /a/b/c/d.

        @return: a list of strs
        """
        # this might be an unnecessarily inefficient implementation but it will
        # work on win32 and for zipfiles; later I will deterimine if the
        # obvious fast implemenation does the right thing too
        f = self
        p: _Self = f.parent()  # type:ignore[assignment]
        segments: List[AnyStr] = []
        while f != ancestor and p != f:
            segments[0:0] = [f.basename()]
            f = p
            p = p.parent()  # type:ignore[assignment]
        if f == ancestor and segments:
            return segments
        raise ValueError(f"{ancestor!r} not parent of {self!r}")

    # new in 8.0
    def __hash__(self) -> int:
        """
        Hash the same as another L{AbstractFilePath} with the same path as mine.
        """
        return hash((self.__class__, self.path))

    # pending deprecation in 8.0
    def getmtime(self) -> int:
        """
        Deprecated.  Use getModificationTime instead.
        """
        return int(self.getModificationTime())

    def getatime(self) -> int:
        """
        Deprecated.  Use getAccessTime instead.
        """
        return int(self.getAccessTime())

    def getctime(self) -> int:
        """
        Deprecated.  Use getStatusChangeTime instead.
        """
        return int(self.getStatusChangeTime())


class RWX(FancyEqMixin):
    """
    A class representing read/write/execute permissions for a single user
    category (i.e. user/owner, group, or other/world).  Instantiate with
    three boolean values: readable? writable? executable?.

    @type read: C{bool}
    @ivar read: Whether permission to read is given

    @type write: C{bool}
    @ivar write: Whether permission to write is given

    @type execute: C{bool}
    @ivar execute: Whether permission to execute is given

    @since: 11.1
    """

    compareAttributes = ("read", "write", "execute")

    def __init__(self, readable: bool, writable: bool, executable: bool) -> None:
        self.read = readable
        self.write = writable
        self.execute = executable

    def __repr__(self) -> str:
        return "RWX(read={}, write={}, execute={})".format(
            self.read,
            self.write,
            self.execute,
        )

    def shorthand(self) -> str:
        """
        Returns a short string representing the permission bits.  Looks like
        part of what is printed by command line utilities such as 'ls -l'
        (e.g. 'rwx')

        @return: The shorthand string.
        @rtype: L{str}
        """
        returnval = ["r", "w", "x"]
        i = 0
        for val in (self.read, self.write, self.execute):
            if not val:
                returnval[i] = "-"
            i += 1
        return "".join(returnval)


class Permissions(FancyEqMixin):
    """
    A class representing read/write/execute permissions.  Instantiate with any
    portion of the file's mode that includes the permission bits.

    @type user: L{RWX}
    @ivar user: User/Owner permissions

    @type group: L{RWX}
    @ivar group: Group permissions

    @type other: L{RWX}
    @ivar other: Other/World permissions

    @since: 11.1
    """

    compareAttributes = ("user", "group", "other")

    def __init__(self, statModeInt: int) -> None:
        self.user, self.group, self.other = (
            RWX(*(statModeInt & bit > 0 for bit in bitGroup))
            for bitGroup in [
                [S_IRUSR, S_IWUSR, S_IXUSR],
                [S_IRGRP, S_IWGRP, S_IXGRP],
                [S_IROTH, S_IWOTH, S_IXOTH],
            ]
        )

    def __repr__(self) -> str:
        return f"[{str(self.user)} | {str(self.group)} | {str(self.other)}]"

    def shorthand(self) -> str:
        """
        Returns a short string representing the permission bits.  Looks like
        what is printed by command line utilities such as 'ls -l'
        (e.g. 'rwx-wx--x')

        @return: The shorthand string.
        @rtype: L{str}
        """
        return "".join([x.shorthand() for x in (self.user, self.group, self.other)])


def _asFilesystemBytes(path: Union[bytes, str], encoding: Optional[str] = "") -> bytes:
    """
    Return C{path} as a string of L{bytes} suitable for use on this system's
    filesystem.

    @param path: The path to be made suitable.
    @type path: L{bytes} or L{unicode}
    @param encoding: The encoding to use if coercing to L{bytes}. If none is
        given, L{sys.getfilesystemencoding} is used.

    @return: L{bytes}
    """
    if isinstance(path, bytes):
        return path
    else:
        if not encoding:
            encoding = sys.getfilesystemencoding()
        return path.encode(encoding, errors="surrogateescape")


def _asFilesystemText(path: Union[bytes, str], encoding: Optional[str] = None) -> str:
    """
    Return C{path} as a string of L{unicode} suitable for use on this system's
    filesystem.

    @param path: The path to be made suitable.
    @type path: L{bytes} or L{unicode}

    @param encoding: The encoding to use if coercing to L{unicode}. If none
        is given, L{sys.getfilesystemencoding} is used.

    @return: L{unicode}
    """
    if isinstance(path, str):
        return path
    else:
        if encoding is None:
            encoding = sys.getfilesystemencoding()
        return path.decode(encoding, errors="surrogateescape")


def _coerceToFilesystemEncoding(
    path: AnyStr, newpath: Union[bytes, str], encoding: Optional[str] = None
) -> AnyStr:
    """
    Return a C{newpath} that is suitable for joining to C{path}.

    @param path: The path that it should be suitable for joining to.
    @param newpath: The new portion of the path to be coerced if needed.
    @param encoding: If coerced, the encoding that will be used.
    """
    if isinstance(path, bytes):
        return _asFilesystemBytes(newpath, encoding=encoding)
    else:
        return _asFilesystemText(newpath, encoding=encoding)


@comparable
@implementer(IFilePath)
class FilePath(AbstractFilePath[AnyStr]):
    """
    I am a path on the filesystem that only permits 'downwards' access.

    Instantiate me with a pathname (for example,
    FilePath('/home/myuser/public_html')) and I will attempt to only provide
    access to files which reside inside that path.  I may be a path to a file,
    a directory, or a file which does not exist.

    The correct way to use me is to instantiate me, and then do ALL filesystem
    access through me.  In other words, do not import the 'os' module; if you
    need to open a file, call my 'open' method.  If you need to list a
    directory, call my 'path' method.

    Even if you pass me a relative path, I will convert that to an absolute
    path internally.

    The type of C{path} when instantiating decides the mode of the L{FilePath}.
    That is, C{FilePath(b"/")} will return a L{bytes} mode L{FilePath}, and
    C{FilePath(u"/")} will return a L{unicode} mode L{FilePath}.
    C{FilePath("/")} will return a L{bytes} mode L{FilePath} on Python 2, and a
    L{unicode} mode L{FilePath} on Python 3.

    Methods that return a new L{FilePath} use the type of the given subpath to
    decide its mode. For example, C{FilePath(b"/").child(u"tmp")} will return a
    L{unicode} mode L{FilePath}.

    @type alwaysCreate: L{bool}
    @ivar alwaysCreate: When opening this file, only succeed if the file does
        not already exist.

    @ivar path: The path from which 'downward' traversal is permitted.
    """

    _statinfo = None
    path: AnyStr

    def __init__(self, path: AnyStr, alwaysCreate: bool = False) -> None:
        """
        Convert a path string to an absolute path if necessary and initialize
        the L{FilePath} with the result.
        """
        self.path = abspath(path)
        self.alwaysCreate = alwaysCreate

    if TYPE_CHECKING:

        def sibling(self: _Self, path: OtherAnyStr) -> FilePath[OtherAnyStr]:
            ...

        def descendant(self, segments: Sequence[OtherAnyStr]) -> FilePath[OtherAnyStr]:
            ...

        def parents(self) -> Iterable[FilePath[AnyStr]]:
            ...

        # provided by @comparable
        def __gt__(self, other: object) -> bool:
            ...

        def __ge__(self, other: object) -> bool:
            ...

        def __lt__(self, other: object) -> bool:
            ...

        def __le__(self, other: object) -> bool:
            ...

        def __eq__(self, other: object) -> bool:
            ...

        def __ne__(self, other: object) -> bool:
            ...

    def clonePath(
        self, path: OtherAnyStr, alwaysCreate: bool = False
    ) -> FilePath[OtherAnyStr]:
        """
        Make an object of the same type as this FilePath, but with path of
        C{path}.
        """
        return FilePath(path)

    def __getstate__(self) -> Dict[str, object]:
        """
        Support serialization by discarding cached L{os.stat} results and
        returning everything else.
        """
        d = self.__dict__.copy()
        if "_statinfo" in d:
            del d["_statinfo"]
        return d

    @property
    def sep(self) -> AnyStr:
        """
        Return a filesystem separator.

        @return: The native filesystem separator.
        @returntype: The same type as C{self.path}.
        """
        return _coerceToFilesystemEncoding(self.path, os.sep)

    def _asBytesPath(self, encoding: Optional[str] = None) -> bytes:
        """
        Return the path of this L{FilePath} as bytes.

        @param encoding: The encoding to use if coercing to L{bytes}. If none is
            given, L{sys.getfilesystemencoding} is used.

        @return: L{bytes}
        """
        return _asFilesystemBytes(self.path, encoding=encoding)

    def _asTextPath(self, encoding: Optional[str] = None) -> str:
        """
        Return the path of this L{FilePath} as text.

        @param encoding: The encoding to use if coercing to L{unicode}. If none
            is given, L{sys.getfilesystemencoding} is used.

        @return: L{unicode}
        """
        return _asFilesystemText(self.path, encoding=encoding)

    def asBytesMode(self, encoding: Optional[str] = None) -> FilePath[bytes]:
        """
        Return this L{FilePath} in L{bytes}-mode.

        @param encoding: The encoding to use if coercing to L{bytes}. If none is
            given, L{sys.getfilesystemencoding} is used.

        @return: L{bytes} mode L{FilePath}
        """
        if isinstance(self.path, str):
            return self.clonePath(self._asBytesPath(encoding=encoding))
        return self

    def asTextMode(self, encoding: Optional[str] = None) -> FilePath[str]:
        """
        Return this L{FilePath} in L{unicode}-mode.

        @param encoding: The encoding to use if coercing to L{unicode}. If none
            is given, L{sys.getfilesystemencoding} is used.

        @return: L{unicode} mode L{FilePath}
        """
        if isinstance(self.path, bytes):
            return self.clonePath(self._asTextPath(encoding=encoding))
        return self

    def _getPathAsSameTypeAs(self, pattern: OtherAnyStr) -> OtherAnyStr:
        """
        If C{pattern} is C{bytes}, return L{FilePath.path} as L{bytes}.
        Otherwise, return L{FilePath.path} as L{unicode}.

        @param pattern: The new element of the path that L{FilePath.path} may
            need to be coerced to match.
        """
        if isinstance(pattern, bytes):
            return self._asBytesPath()
        else:
            return self._asTextPath()

    def child(self, path: OtherAnyStr) -> FilePath[OtherAnyStr]:
        """
        Create and return a new L{FilePath} representing a path contained by
        C{self}.

        @param path: The base name of the new L{FilePath}.  If this contains
            directory separators or parent references it will be rejected.
        @type path: L{bytes} or L{unicode}

        @raise InsecurePath: If the result of combining this path with C{path}
            would result in a path which is not a direct child of this path.

        @return: The child path.
        @rtype: L{FilePath} with a mode equal to the type of C{path}.
        """
        colon = _coerceToFilesystemEncoding(path, ":")
        sep = _coerceToFilesystemEncoding(path, os.sep)
        ourPath = self._getPathAsSameTypeAs(path)

        if platform.isWindows() and path.count(colon):
            # Catch paths like C:blah that don't have a slash
            raise InsecurePath(f"{path!r} contains a colon.")

        norm = normpath(path)
        if sep in norm:
            raise InsecurePath(f"{path!r} contains one or more directory separators")

        newpath = abspath(joinpath(ourPath, norm))
        if not newpath.startswith(ourPath):
            raise InsecurePath(f"{newpath!r} is not a child of {ourPath!r}")
        return self.clonePath(newpath)

    def preauthChild(self, path: OtherAnyStr) -> FilePath[OtherAnyStr]:
        """
        Use me if C{path} might have slashes in it, but you know they're safe.

        @param path: A relative path (ie, a path not starting with C{"/"})
            which will be interpreted as a child or descendant of this path.
        @type path: L{bytes} or L{unicode}

        @return: The child path.
        @rtype: L{FilePath} with a mode equal to the type of C{path}.
        """
        ourPath = self._getPathAsSameTypeAs(path)

        newpath = abspath(joinpath(ourPath, normpath(path)))
        if not newpath.startswith(ourPath):
            raise InsecurePath(f"{newpath!r} is not a child of {ourPath!r}")
        return self.clonePath(newpath)

    def childSearchPreauth(
        self, *paths: OtherAnyStr
    ) -> Optional[FilePath[OtherAnyStr]]:
        """
        Return my first existing child with a name in C{paths}.

        C{paths} is expected to be a list of *pre-secured* path fragments;
        in most cases this will be specified by a system administrator and not
        an arbitrary user.

        If no appropriately-named children exist, this will return L{None}.

        @return: L{None} or the child path.
        @rtype: L{None} or L{FilePath}
        """
        for child in paths:
            p = self._getPathAsSameTypeAs(child)
            jp = joinpath(p, child)
            if exists(jp):
                return self.clonePath(jp)
        return None

    def siblingExtensionSearch(
        self, *exts: OtherAnyStr
    ) -> Optional[FilePath[OtherAnyStr]]:
        """
        Attempt to return a path with my name, given multiple possible
        extensions.

        Each extension in C{exts} will be tested and the first path which
        exists will be returned.  If no path exists, L{None} will be returned.
        If C{''} is in C{exts}, then if the file referred to by this path
        exists, C{self} will be returned.

        The extension '*' has a magic meaning, which means "any path that
        begins with C{self.path + '.'} is acceptable".
        """
        for ext in exts:
            if not ext and self.exists():
                return self.clonePath(self._getPathAsSameTypeAs(ext))

            p = self._getPathAsSameTypeAs(ext)
            star = _coerceToFilesystemEncoding(ext, "*")
            dot = _coerceToFilesystemEncoding(ext, ".")

            if ext == star:
                basedot = basename(p) + dot
                for fn in listdir(dirname(p)):
                    if fn.startswith(basedot):
                        return self.clonePath(joinpath(dirname(p), fn))
            p2 = p + ext
            if exists(p2):
                return self.clonePath(p2)
        return None

    def realpath(self) -> FilePath[AnyStr]:
        """
        Returns the absolute target as a L{FilePath} if self is a link, self
        otherwise.

        The absolute link is the ultimate file or directory the
        link refers to (for instance, if the link refers to another link, and
        another...).  If the filesystem does not support symlinks, or
        if the link is cyclical, raises a L{LinkError}.

        Behaves like L{os.path.realpath} in that it does not resolve link
        names in the middle (ex. /x/y/z, y is a link to w - realpath on z
        will return /x/y/z, not /x/w/z).

        @return: L{FilePath} of the target path.
        @rtype: L{FilePath}
        @raises LinkError: if links are not supported or links are cyclical.
        """
        if self.islink():
            result = os.path.realpath(self.path)
            if result == self.path:
                raise LinkError("Cyclical link - will loop forever")
            return self.clonePath(result)
        return self

    def siblingExtension(self, ext: OtherAnyStr) -> FilePath[OtherAnyStr]:
        """
        Attempt to return a path with my name, given the extension at C{ext}.

        @param ext: File-extension to search for.
        @type ext: L{bytes} or L{unicode}

        @return: The sibling path.
        @rtype: L{FilePath} with the same mode as the type of C{ext}.
        """
        ourPath = self._getPathAsSameTypeAs(ext)
        return self.clonePath(ourPath + ext)

    def linkTo(self, linkFilePath: FilePath[AnyStr]) -> None:
        """
        Creates a symlink to self to at the path in the L{FilePath}
        C{linkFilePath}.

        Only works on posix systems due to its dependence on
        L{os.symlink}.  Propagates L{OSError}s up from L{os.symlink} if
        C{linkFilePath.parent()} does not exist, or C{linkFilePath} already
        exists.

        @param linkFilePath: a FilePath representing the link to be created.
        @type linkFilePath: L{FilePath}
        """
        os.symlink(self.path, linkFilePath.path)

    def open(self, mode: FileMode = "r") -> IO[bytes]:
        """
        Open this file using C{mode} or for writing if C{alwaysCreate} is
        C{True}.

        In all cases the file is opened in binary mode, so it is not necessary
        to include C{"b"} in C{mode}.

        @param mode: The mode to open the file in.  Default is C{"r"}.
        @raises AssertionError: If C{"a"} is included in the mode and
            C{alwaysCreate} is C{True}.
        @return: An open file-like object.
        """
        if self.alwaysCreate:
            assert "a" not in mode, (
                "Appending not supported when " "alwaysCreate == True"
            )
            return self.create()
        # Make sure we open with exactly one "b" in the mode.
        return open(self.path, mode.replace("b", "") + "b")

    # stat methods below

    def restat(self, reraise: bool = True) -> None:
        """
        Re-calculate cached effects of 'stat'.  To refresh information on this
        path after you know the filesystem may have changed, call this method.

        @param reraise: a boolean.  If true, re-raise exceptions from
            L{os.stat}; otherwise, mark this path as not existing, and remove
            any cached stat information.

        @raise Exception: If C{reraise} is C{True} and an exception occurs
            while reloading metadata.
        """
        try:
            self._statinfo = stat(self.path)
        except OSError:
            self._statinfo = None
            if reraise:
                raise

    def changed(self) -> None:
        """
        Clear any cached information about the state of this path on disk.

        @since: 10.1.0
        """
        self._statinfo = None

    def chmod(self, mode: int) -> None:
        """
        Changes the permissions on self, if possible.  Propagates errors from
        L{os.chmod} up.

        @param mode: integer representing the new permissions desired (same as
            the command line chmod)
        @type mode: L{int}
        """
        os.chmod(self.path, mode)

    def getsize(self) -> int:
        """
        Retrieve the size of this file in bytes.

        @return: The size of the file at this file path in bytes.
        @raise Exception: if the size cannot be obtained.
        @rtype: L{int}
        """
        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return st.st_size

    def getModificationTime(self) -> float:
        """
        Retrieve the time of last access from this file.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """
        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return float(st.st_mtime)

    def getStatusChangeTime(self) -> float:
        """
        Retrieve the time of the last status change for this file.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """
        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return float(st.st_ctime)

    def getAccessTime(self) -> float:
        """
        Retrieve the time that this file was last accessed.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """
        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return float(st.st_atime)

    def getInodeNumber(self) -> int:
        """
        Retrieve the file serial number, also called inode number, which
        distinguishes this file from all other files on the same device.

        @raise NotImplementedError: if the platform is Windows, since the
            inode number would be a dummy value for all files in Windows
        @return: a number representing the file serial number
        @rtype: L{int}
        @since: 11.0
        """
        if platform.isWindows():
            raise NotImplementedError

        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return st.st_ino

    def getDevice(self) -> int:
        """
        Retrieves the device containing the file.  The inode number and device
        number together uniquely identify the file, but the device number is
        not necessarily consistent across reboots or system crashes.

        @raise NotImplementedError: if the platform is Windows, since the
            device number would be 0 for all partitions on a Windows platform

        @return: a number representing the device
        @rtype: L{int}

        @since: 11.0
        """
        if platform.isWindows():
            raise NotImplementedError

        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return st.st_dev

    def getNumberOfHardLinks(self) -> int:
        """
        Retrieves the number of hard links to the file.

        This count keeps track of how many directories have entries for this
        file. If the count is ever decremented to zero then the file itself is
        discarded as soon as no process still holds it open.  Symbolic links
        are not counted in the total.

        @raise NotImplementedError: if the platform is Windows, since Windows
            doesn't maintain a link count for directories, and L{os.stat} does
            not set C{st_nlink} on Windows anyway.
        @return: the number of hard links to the file
        @rtype: L{int}
        @since: 11.0
        """
        if platform.isWindows():
            raise NotImplementedError

        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return st.st_nlink

    def getUserID(self) -> int:
        """
        Returns the user ID of the file's owner.

        @raise NotImplementedError: if the platform is Windows, since the UID
            is always 0 on Windows
        @return: the user ID of the file's owner
        @rtype: L{int}
        @since: 11.0
        """
        if platform.isWindows():
            raise NotImplementedError

        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return st.st_uid

    def getGroupID(self) -> int:
        """
        Returns the group ID of the file.

        @raise NotImplementedError: if the platform is Windows, since the GID
            is always 0 on windows
        @return: the group ID of the file
        @rtype: L{int}
        @since: 11.0
        """
        if platform.isWindows():
            raise NotImplementedError

        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return st.st_gid

    def getPermissions(self) -> Permissions:
        """
        Returns the permissions of the file.  Should also work on Windows,
        however, those permissions may not be what is expected in Windows.

        @return: the permissions for the file
        @rtype: L{Permissions}
        @since: 11.1
        """
        st = self._statinfo
        if not st:
            self.restat()
            st = self._statinfo
        assert st is not None
        return Permissions(S_IMODE(st.st_mode))

    def exists(self) -> bool:
        """
        Check if this L{FilePath} exists.

        @return: C{True} if the stats of C{path} can be retrieved successfully,
            C{False} in the other cases.
        @rtype: L{bool}
        """
        if self._statinfo:
            return True
        else:
            self.restat(False)
            if self._statinfo:
                return True
            else:
                return False

    def isdir(self) -> bool:
        """
        Check if this L{FilePath} refers to a directory.

        @return: C{True} if this L{FilePath} refers to a directory, C{False}
            otherwise.
        @rtype: L{bool}
        """
        st = self._statinfo
        if not st:
            self.restat(False)
            st = self._statinfo
            if not st:
                return False
        return S_ISDIR(st.st_mode)

    def isfile(self) -> bool:
        """
        Check if this file path refers to a regular file.

        @return: C{True} if this L{FilePath} points to a regular file (not a
            directory, socket, named pipe, etc), C{False} otherwise.
        @rtype: L{bool}
        """
        st = self._statinfo
        if not st:
            self.restat(False)
            st = self._statinfo
            if not st:
                return False
        return S_ISREG(st.st_mode)

    def isBlockDevice(self) -> bool:
        """
        Returns whether the underlying path is a block device.

        @return: C{True} if it is a block device, C{False} otherwise
        @rtype: L{bool}
        @since: 11.1
        """
        st = self._statinfo
        if not st:
            self.restat(False)
            st = self._statinfo
            if not st:
                return False
        return S_ISBLK(st.st_mode)

    def isSocket(self) -> bool:
        """
        Returns whether the underlying path is a socket.

        @return: C{True} if it is a socket, C{False} otherwise
        @rtype: L{bool}
        @since: 11.1
        """
        st = self._statinfo
        if not st:
            self.restat(False)
            st = self._statinfo
            if not st:
                return False
        return S_ISSOCK(st.st_mode)

    def islink(self) -> bool:
        """
        Check if this L{FilePath} points to a symbolic link.

        @return: C{True} if this L{FilePath} points to a symbolic link,
            C{False} otherwise.
        @rtype: L{bool}
        """
        # We can't use cached stat results here, because that is the stat of
        # the destination - (see #1773) which in *every case* but this one is
        # the right thing to use.  We could call lstat here and use that, but
        # it seems unlikely we'd actually save any work that way.  -glyph
        return islink(self.path)

    def isabs(self) -> bool:
        """
        Check if this L{FilePath} refers to an absolute path.

        This always returns C{True}.

        @return: C{True}, always.
        @rtype: L{bool}
        """
        return isabs(self.path)

    def listdir(self) -> List[AnyStr]:
        """
        List the base names of the direct children of this L{FilePath}.

        @return: A L{list} of L{bytes}/L{unicode} giving the names of the
            contents of the directory this L{FilePath} refers to. These names
            are relative to this L{FilePath}.
        @rtype: L{list}

        @raise OSError: Any exception the platform L{os.listdir} implementation
            may raise.
        """
        return listdir(self.path)

    def splitext(self) -> Tuple[AnyStr, AnyStr]:
        """
        Split the file path into a pair C{(root, ext)} such that
        C{root + ext == path}.

        @return: Tuple where the first item is the filename and second item is
            the file extension. See Python docs for L{os.path.splitext}.
        @rtype: L{tuple}
        """
        return splitext(self.path)

    def __repr__(self) -> str:
        return f"FilePath({self.path!r})"

    def touch(self) -> None:
        """
        Updates the access and last modification times of the file at this
        file path to the current time. Also creates the file if it does not
        already exist.

        @raise Exception: if unable to create or modify the last modification
            time of the file.
        """
        try:
            self.open("a").close()
        except OSError:
            pass
        utime(self.path, None)

    def remove(self) -> None:
        """
        Removes the file or directory that is represented by self.  If
        C{self.path} is a directory, recursively remove all its children
        before removing the directory. If it's a file or link, just delete it.
        """
        if self.isdir() and not self.islink():
            for child in self.children():
                child.remove()
            os.rmdir(self.path)
        else:
            os.remove(self.path)
        self.changed()

    def makedirs(self, ignoreExistingDirectory: bool = False) -> None:
        """
        Create all directories not yet existing in C{path} segments, using
        L{os.makedirs}.

        @param ignoreExistingDirectory: Don't raise L{OSError} if directory
            already exists.
        @type ignoreExistingDirectory: L{bool}

        @return: L{None}
        """
        try:
            os.makedirs(self.path)
        except OSError as e:
            if not (
                e.errno == errno.EEXIST and ignoreExistingDirectory and self.isdir()
            ):
                raise

    def globChildren(self, pattern: OtherAnyStr) -> List[FilePath[OtherAnyStr]]:
        """
        Assuming I am representing a directory, return a list of FilePaths
        representing my children that match the given pattern.

        @param pattern: A glob pattern to use to match child paths.
        @type pattern: L{unicode} or L{bytes}

        @return: A L{list} of matching children.
        @rtype: L{list} of L{FilePath}, with the mode of C{pattern}'s type
        """
        sep = _coerceToFilesystemEncoding(pattern, os.sep)
        ourPath = self._getPathAsSameTypeAs(pattern)

        import glob

        path = ourPath[-1] == sep and ourPath + pattern or sep.join([ourPath, pattern])
        return [self.clonePath(p) for p in glob.glob(path)]

    def basename(self) -> AnyStr:
        """
        Retrieve the final component of the file path's path (everything
        after the final path separator).

        @return: The final component of the L{FilePath}'s path (Everything
            after the final path separator).
        @rtype: the same type as this L{FilePath}'s C{path} attribute
        """
        return basename(self.path)

    def dirname(self) -> AnyStr:
        """
        Retrieve all of the components of the L{FilePath}'s path except the
        last one (everything up to the final path separator).

        @return: All of the components of the L{FilePath}'s path except the
            last one (everything up to the final path separator).
        @rtype: the same type as this L{FilePath}'s C{path} attribute
        """
        return dirname(self.path)

    def parent(self) -> FilePath[AnyStr]:
        """
        A file path for the directory containing the file at this file path.

        @return: A L{FilePath} representing the path which directly contains
            this L{FilePath}.
        @rtype: L{FilePath}
        """
        return self.clonePath(self.dirname())

    def setContent(self, content: bytes, ext: Union[str, bytes] = ".new") -> None:
        """
        Replace the file at this path with a new file that contains the given
        bytes, trying to avoid data-loss in the meanwhile.

        On UNIX-like platforms, this method does its best to ensure that by the
        time this method returns, either the old contents I{or} the new
        contents of the file will be present at this path for subsequent
        readers regardless of premature device removal, program crash, or power
        loss, making the following assumptions:

            - your filesystem is journaled (i.e. your filesystem will not
              I{itself} lose data due to power loss)

            - your filesystem's C{rename()} is atomic

            - your filesystem will not discard new data while preserving new
              metadata (see U{http://mjg59.livejournal.com/108257.html} for
              more detail)

        On most versions of Windows there is no atomic C{rename()} (see
        U{http://bit.ly/win32-overwrite} for more information), so this method
        is slightly less helpful.  There is a small window where the file at
        this path may be deleted before the new file is moved to replace it:
        however, the new file will be fully written and flushed beforehand so
        in the unlikely event that there is a crash at that point, it should be
        possible for the user to manually recover the new version of their
        data.  In the future, Twisted will support atomic file moves on those
        versions of Windows which I{do} support them: see U{Twisted ticket
        3004<http://twistedmatrix.com/trac/ticket/3004>}.

        This method should be safe for use by multiple concurrent processes,
        but note that it is not easy to predict which process's contents will
        ultimately end up on disk if they invoke this method at close to the
        same time.

        @param content: The desired contents of the file at this path.
        @type content: L{bytes}

        @param ext: An extension to append to the temporary filename used to
            store the bytes while they are being written.  This can be used to
            make sure that temporary files can be identified by their suffix,
            for cleanup in case of crashes.
        @type ext: L{bytes}
        """
        sib = self.temporarySibling(ext)
        with sib.open("w") as f:
            f.write(content)
        if platform.isWindows() and exists(self.path):
            os.unlink(self.path)
        os.rename(sib.path, self.asBytesMode().path)

    def __cmp__(self, other: object) -> int:
        if not isinstance(other, FilePath):
            return NotImplemented
        return cmp(self.path, other.path)

    def createDirectory(self) -> None:
        """
        Create the directory the L{FilePath} refers to.

        @see: L{makedirs}

        @raise OSError: If the directory cannot be created.
        """
        os.mkdir(self.path)

    def requireCreate(self, val: bool = True) -> None:
        """
        Sets the C{alwaysCreate} variable.

        @param val: C{True} or C{False}, indicating whether opening this path
            will be required to create the file or not.
        @type val: L{bool}

        @return: L{None}
        """
        self.alwaysCreate = val

    def create(self) -> IO[bytes]:
        """
        Exclusively create a file, only if this file previously did not exist.

        @return: A file-like object opened from this path.
        """
        fdint = os.open(self.path, _CREATE_FLAGS)

        # XXX TODO: 'name' attribute of returned files is not mutable or
        # settable via fdopen, so this file is slightly less functional than the
        # one returned from 'open' by default.  send a patch to Python...

        return cast(IO[bytes], os.fdopen(fdint, "w+b"))

    @overload
    def temporarySibling(self) -> FilePath[AnyStr]:
        ...

    @overload
    def temporarySibling(
        self, extension: Optional[OtherAnyStr]
    ) -> FilePath[OtherAnyStr]:
        ...

    def temporarySibling(
        self, extension: Optional[OtherAnyStr] = None
    ) -> FilePath[OtherAnyStr]:
        """
        Construct a path referring to a sibling of this path.

        The resulting path will be unpredictable, so that other subprocesses
        should neither accidentally attempt to refer to the same path before it
        is created, nor they should other processes be able to guess its name
        in advance.

        @param extension: A suffix to append to the created filename.  (Note
            that if you want an extension with a '.' you must include the '.'
            yourself.)
        @type extension: L{bytes} or L{unicode}

        @return: a path object with the given extension suffix, C{alwaysCreate}
            set to True.
        @rtype: L{FilePath} with a mode equal to the type of C{extension}
        """
        ext: OtherAnyStr
        if extension is None:
            # It's not possible to provide a default type argument which is why
            # the overload is required.
            ext = self.path[0:0]  # type:ignore[assignment]
        else:
            ext = extension
        ourPath = self._getPathAsSameTypeAs(ext)
        sib = self.sibling(
            _secureEnoughString(ourPath) + self.clonePath(ourPath).basename() + ext
        )
        sib.requireCreate()
        return sib

    _chunkSize = 2**2**2**2

    def copyTo(
        self, destination: FilePath[OtherAnyStr], followLinks: bool = True
    ) -> None:
        """
        Copies self to destination.

        If self doesn't exist, an OSError is raised.

        If self is a directory, this method copies its children (but not
        itself) recursively to destination - if destination does not exist as a
        directory, this method creates it.  If destination is a file, an
        IOError will be raised.

        If self is a file, this method copies it to destination.  If
        destination is a file, this method overwrites it.  If destination is a
        directory, an IOError will be raised.

        If self is a link (and followLinks is False), self will be copied
        over as a new symlink with the same target as returned by os.readlink.
        That means that if it is absolute, both the old and new symlink will
        link to the same thing.  If it's relative, then perhaps not (and
        it's also possible that this relative link will be broken).

        File/directory permissions and ownership will NOT be copied over.

        If followLinks is True, symlinks are followed so that they're treated
        as their targets.  In other words, if self is a link, the link's target
        will be copied.  If destination is a link, self will be copied to the
        destination's target (the actual destination will be destination's
        target).  Symlinks under self (if self is a directory) will be
        followed and its target's children be copied recursively.

        If followLinks is False, symlinks will be copied over as symlinks.

        @param destination: the destination (a FilePath) to which self
            should be copied
        @param followLinks: whether symlinks in self should be treated as links
            or as their targets
        """
        if self.islink() and not followLinks:
            os.symlink(os.readlink(self.path), destination.path)
            return
        # XXX TODO: *thorough* audit and documentation of the exact desired
        # semantics of this code.  Right now the behavior of existent
        # destination symlinks is convenient, and quite possibly correct, but
        # its security properties need to be explained.
        if self.isdir():
            if not destination.exists():
                destination.createDirectory()
            for child in self.children():
                destChild = destination.child(child.basename())
                child.copyTo(destChild, followLinks)
        elif self.isfile():
            with destination.open("w") as writefile, self.open() as readfile:
                while 1:
                    # XXX TODO: optionally use os.open, os.read and
                    # O_DIRECT and use os.fstatvfs to determine chunk sizes
                    # and make *****sure**** copy is page-atomic; the
                    # following is good enough for 99.9% of everybody and
                    # won't take a week to audit though.
                    chunk = readfile.read(self._chunkSize)
                    writefile.write(chunk)
                    if len(chunk) < self._chunkSize:
                        break
        elif not self.exists():
            raise OSError(errno.ENOENT, "No such file or directory")
        else:
            # If you see the following message because you want to copy
            # symlinks, fifos, block devices, character devices, or unix
            # sockets, please feel free to add support to do sensible things in
            # reaction to those types!
            raise NotImplementedError("Only copying of files and directories supported")

    def moveTo(
        self, destination: FilePath[OtherAnyStr], followLinks: bool = True
    ) -> None:
        """
        Move self to destination - basically renaming self to whatever
        destination is named.

        If destination is an already-existing directory,
        moves all children to destination if destination is empty.  If
        destination is a non-empty directory, or destination is a file, an
        OSError will be raised.

        If moving between filesystems, self needs to be copied, and everything
        that applies to copyTo applies to moveTo.

        @param destination: the destination (a FilePath) to which self
            should be copied
        @param followLinks: whether symlinks in self should be treated as links
            or as their targets (only applicable when moving between
            filesystems)
        """
        try:
            os.rename(self._getPathAsSameTypeAs(destination.path), destination.path)
        except OSError as ose:
            if ose.errno == errno.EXDEV:
                # man 2 rename, ubuntu linux 5.10 "breezy":

                #   oldpath and newpath are not on the same mounted filesystem.
                #   (Linux permits a filesystem to be mounted at multiple
                #   points, but rename(2) does not work across different mount
                #   points, even if the same filesystem is mounted on both.)

                # that means it's time to copy trees of directories!
                secsib = destination.temporarySibling()
                self.copyTo(secsib, followLinks)  # slow
                secsib.moveTo(destination, followLinks)  # visible

                # done creating new stuff.  let's clean me up.
                mysecsib = self.temporarySibling()
                self.moveTo(mysecsib, followLinks)  # visible
                mysecsib.remove()  # slow
            else:
                raise
        else:
            self.changed()
            destination.changed()
