# -*- test-case-name: twisted.python.test.test_zippath -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module contains implementations of L{IFilePath} for zip files.

See the constructor of L{ZipArchive} for use.
"""
from __future__ import annotations

import errno
import os
import time
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    AnyStr,
    Dict,
    Generic,
    Iterable,
    List,
    Tuple,
    TypeVar,
    Union,
)
from zipfile import ZipFile

from zope.interface import implementer

from typing_extensions import Literal, Self

from twisted.python.compat import cmp, comparable
from twisted.python.filepath import (
    AbstractFilePath,
    FilePath,
    IFilePath,
    OtherAnyStr,
    UnlistableError,
    _coerceToFilesystemEncoding,
)

ZIP_PATH_SEP = "/"  # In zipfiles, "/" is universally used as the
# path separator, regardless of platform.

_ArchiveStr = TypeVar("_ArchiveStr", bytes, str)
_ZipStr = TypeVar("_ZipStr", bytes, str)
_ZipSelf = TypeVar("_ZipSelf", bound="ZipPath[Any, Any]")


@comparable
@implementer(IFilePath)
class ZipPath(Generic[_ZipStr, _ArchiveStr], AbstractFilePath[_ZipStr]):
    """
    I represent a file or directory contained within a zip file.
    """

    path: _ZipStr

    def __init__(
        self, archive: ZipArchive[_ArchiveStr], pathInArchive: _ZipStr
    ) -> None:
        """
        Don't construct me directly.  Use C{ZipArchive.child()}.

        @param archive: a L{ZipArchive} instance.

        @param pathInArchive: a ZIP_PATH_SEP-separated string.
        """
        self.archive: ZipArchive[_ArchiveStr] = archive
        self.pathInArchive: _ZipStr = pathInArchive
        self._nativePathInArchive: _ArchiveStr = _coerceToFilesystemEncoding(
            archive._zipfileFilename, pathInArchive
        )

        # self.path pretends to be os-specific because that's the way the
        # 'zipimport' module does it.
        sep = _coerceToFilesystemEncoding(pathInArchive, ZIP_PATH_SEP)
        archiveFilename: _ZipStr = _coerceToFilesystemEncoding(
            pathInArchive, archive._zipfileFilename
        )
        segments: List[_ZipStr] = self.pathInArchive.split(sep)
        fakePath: _ZipStr = os.path.join(archiveFilename, *segments)
        self.path: _ZipStr = fakePath

    def __cmp__(self, other: object) -> int:
        if not isinstance(other, ZipPath):
            return NotImplemented
        return cmp(
            (self.archive, self.pathInArchive), (other.archive, other.pathInArchive)
        )

    def __repr__(self) -> str:
        parts: List[_ZipStr]
        parts = [
            _coerceToFilesystemEncoding(self.sep, os.path.abspath(self.archive.path))
        ]
        parts.extend(self.pathInArchive.split(self.sep))
        ossep = _coerceToFilesystemEncoding(self.sep, os.sep)
        return f"ZipPath({ossep.join(parts)!r})"

    @property
    def sep(self) -> _ZipStr:
        """
        Return a zip directory separator.

        @return: The zip directory separator.
        @returntype: The same type as C{self.path}.
        """
        return _coerceToFilesystemEncoding(self.path, ZIP_PATH_SEP)

    def _nativeParent(
        self,
    ) -> Union[ZipPath[_ZipStr, _ArchiveStr], ZipArchive[_ArchiveStr]]:
        """
        Return parent, discarding our own encoding in favor of whatever the
        archive's is.
        """
        splitup = self.pathInArchive.split(self.sep)
        if len(splitup) == 1:
            return self.archive
        return ZipPath(self.archive, self.sep.join(splitup[:-1]))

    def parent(self) -> Union[ZipPath[_ZipStr, _ArchiveStr], ZipArchive[_ZipStr]]:
        parent = self._nativeParent()
        if isinstance(parent, ZipArchive):
            return ZipArchive(
                _coerceToFilesystemEncoding(self.path, self.archive._zipfileFilename)
            )
        return parent

    if TYPE_CHECKING:

        def parents(
            self,
        ) -> Iterable[Union[ZipPath[_ZipStr, _ArchiveStr], ZipArchive[_ZipStr]]]:
            ...

    def child(self, path: OtherAnyStr) -> ZipPath[OtherAnyStr, _ArchiveStr]:
        """
        Return a new ZipPath representing a path in C{self.archive} which is
        a child of this path.

        @note: Requesting the C{".."} (or other special name) child will not
            cause L{InsecurePath} to be raised since these names do not have
            any special meaning inside a zip archive.  Be particularly
            careful with the C{path} attribute (if you absolutely must use
            it) as this means it may include special names with special
            meaning outside of the context of a zip archive.
        """
        joiner = _coerceToFilesystemEncoding(path, ZIP_PATH_SEP)
        pathInArchive = _coerceToFilesystemEncoding(path, self.pathInArchive)
        return ZipPath(self.archive, joiner.join([pathInArchive, path]))

    def sibling(self, path: OtherAnyStr) -> ZipPath[OtherAnyStr, _ArchiveStr]:
        parent: Union[ZipPath[_ZipStr, _ArchiveStr], ZipArchive[_ZipStr]]
        rightTypedParent: Union[ZipPath[_ZipStr, _ArchiveStr], ZipArchive[_ArchiveStr]]

        parent = self.parent()
        rightTypedParent = self.archive if isinstance(parent, ZipArchive) else parent
        child: ZipPath[OtherAnyStr, _ArchiveStr] = rightTypedParent.child(path)
        return child

    def exists(self) -> bool:
        return self.isdir() or self.isfile()

    def isdir(self) -> bool:
        return self.pathInArchive in self.archive.childmap

    def isfile(self) -> bool:
        return self.pathInArchive in self.archive.zipfile.NameToInfo

    def islink(self) -> bool:
        return False

    def listdir(self) -> List[_ZipStr]:
        if self.exists():
            if self.isdir():
                parentArchivePath: _ArchiveStr = _coerceToFilesystemEncoding(
                    self.archive._zipfileFilename, self.pathInArchive
                )
                return [
                    _coerceToFilesystemEncoding(self.path, each)
                    for each in self.archive.childmap[parentArchivePath].keys()
                ]
            else:
                raise UnlistableError(OSError(errno.ENOTDIR, "Leaf zip entry listed"))
        else:
            raise UnlistableError(
                OSError(errno.ENOENT, "Non-existent zip entry listed")
            )

    def splitext(self) -> Tuple[_ZipStr, _ZipStr]:
        """
        Return a value similar to that returned by C{os.path.splitext}.
        """
        # This happens to work out because of the fact that we use OS-specific
        # path separators in the constructor to construct our fake 'path'
        # attribute.
        return os.path.splitext(self.path)

    def basename(self) -> _ZipStr:
        return self.pathInArchive.split(self.sep)[-1]

    def dirname(self) -> _ZipStr:
        # XXX NOTE: This API isn't a very good idea on filepath, but it's even
        # less meaningful here.
        return self.parent().path

    def open(self, mode: Literal["r", "w"] = "r") -> IO[bytes]:  # type:ignore[override]
        # TODO: liskov substitutability is broken here because the stdlib
        # zipfile does not support appending to files within archives, only to
        # archives themselves; we could fix this by emulating append mode.
        pathInArchive = _coerceToFilesystemEncoding("", self.pathInArchive)
        return self.archive.zipfile.open(pathInArchive, mode=mode)

    def changed(self) -> None:
        pass

    def getsize(self) -> int:
        """
        Retrieve this file's size.

        @return: file size, in bytes
        """
        pathInArchive = _coerceToFilesystemEncoding("", self.pathInArchive)
        return self.archive.zipfile.NameToInfo[pathInArchive].file_size

    def getAccessTime(self) -> float:
        """
        Retrieve this file's last access-time.  This is the same as the last access
        time for the archive.

        @return: a number of seconds since the epoch
        """
        return self.archive.getAccessTime()

    def getModificationTime(self) -> float:
        """
        Retrieve this file's last modification time.  This is the time of
        modification recorded in the zipfile.

        @return: a number of seconds since the epoch.
        """
        pathInArchive = _coerceToFilesystemEncoding("", self.pathInArchive)
        return time.mktime(
            self.archive.zipfile.NameToInfo[pathInArchive].date_time + (0, 0, 0)
        )

    def getStatusChangeTime(self) -> float:
        """
        Retrieve this file's last modification time.  This name is provided for
        compatibility, and returns the same value as getmtime.

        @return: a number of seconds since the epoch.
        """
        return self.getModificationTime()


class ZipArchive(ZipPath[AnyStr, AnyStr]):
    """
    I am a L{FilePath}-like object which can wrap a zip archive as if it were a
    directory.

    It works similarly to L{FilePath} in L{bytes} and L{unicode} handling --
    instantiating with a L{bytes} will return a "bytes mode" L{ZipArchive},
    and instantiating with a L{unicode} will return a "text mode"
    L{ZipArchive}. Methods that return new L{ZipArchive} or L{ZipPath}
    instances will be in the mode of the argument to the creator method,
    converting if required.
    """

    _zipfileFilename: AnyStr

    @property
    def archive(self) -> Self:  # type: ignore[override]
        return self

    def __init__(self, archivePathname: AnyStr) -> None:
        """
        Create a ZipArchive, treating the archive at archivePathname as a zip
        file.

        @param archivePathname: a L{bytes} or L{unicode}, naming a path in the
            filesystem.
        """
        self.path = archivePathname
        self.zipfile = ZipFile(_coerceToFilesystemEncoding("", archivePathname))
        zfname = self.zipfile.filename
        assert (
            zfname is not None
        ), "zipfile must have filename when initialized with a path"
        self._zipfileFilename = _coerceToFilesystemEncoding(archivePathname, zfname)
        self.pathInArchive = _coerceToFilesystemEncoding(archivePathname, "")
        # zipfile is already wasting O(N) memory on cached ZipInfo instances,
        # so there's no sense in trying to do this lazily or intelligently
        self.childmap: Dict[AnyStr, Dict[AnyStr, int]] = {}

        for name in self.zipfile.namelist():
            splitName = _coerceToFilesystemEncoding(self.path, name).split(self.sep)
            for x in range(len(splitName)):
                child = splitName[-x]
                parent = self.sep.join(splitName[:-x])
                if parent not in self.childmap:
                    self.childmap[parent] = {}
                self.childmap[parent][child] = 1
            parent = _coerceToFilesystemEncoding(archivePathname, "")

    def __cmp__(self, other: object) -> int:
        if not isinstance(other, ZipArchive):
            return NotImplemented
        return cmp(self.path, other.path)

    def child(self, path: OtherAnyStr) -> ZipPath[OtherAnyStr, AnyStr]:
        """
        Create a ZipPath pointing at a path within the archive.

        @param path: a L{bytes} or L{unicode} with no path separators in it
            (either '/' or the system path separator, if it's different).
        """
        return ZipPath(self, path)

    def exists(self) -> bool:
        """
        Returns C{True} if the underlying archive exists.
        """
        return FilePath(self._zipfileFilename).exists()

    def getAccessTime(self) -> float:
        """
        Return the archive file's last access time.
        """
        return FilePath(self._zipfileFilename).getAccessTime()

    def getModificationTime(self) -> float:
        """
        Return the archive file's modification time.
        """
        return FilePath(self._zipfileFilename).getModificationTime()

    def getStatusChangeTime(self) -> float:
        """
        Return the archive file's status change time.
        """
        return FilePath(self._zipfileFilename).getStatusChangeTime()

    def __repr__(self) -> str:
        return f"ZipArchive({os.path.abspath(self.path)!r})"


__all__ = ["ZipArchive", "ZipPath"]
