# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases covering L{twisted.python.zippath}.
"""
from __future__ import annotations

import os
import zipfile
from typing import Union

from twisted.python.filepath import _coerceToFilesystemEncoding
from twisted.python.zippath import ZipArchive, ZipPath
from twisted.test.test_paths import AbstractFilePathTests


def zipit(dirname: str | bytes, zfname: str | bytes) -> None:
    """
    Create a zipfile on zfname, containing the contents of dirname'
    """
    coercedDirname = _coerceToFilesystemEncoding("", dirname)
    coercedZfname = _coerceToFilesystemEncoding("", zfname)

    with zipfile.ZipFile(coercedZfname, "w") as zf:
        for (
            root,
            ignored,
            files,
        ) in os.walk(coercedDirname):
            for fname in files:
                fspath = os.path.join(root, fname)
                arcpath = os.path.join(root, fname)[len(dirname) + 1 :]
                zf.write(fspath, arcpath)


class ZipFilePathTests(AbstractFilePathTests):
    """
    Test various L{ZipPath} path manipulations as well as reprs for L{ZipPath}
    and L{ZipArchive}.
    """

    path: ZipArchive[bytes]  # type:ignore[assignment]
    root: ZipArchive[bytes]  # type:ignore[assignment]

    def setUp(self) -> None:
        AbstractFilePathTests.setUp(self)
        zipit(self.cmn, self.cmn + b".zip")
        self.nativecmn = _coerceToFilesystemEncoding("", self.cmn)
        self.path = ZipArchive(self.cmn + b".zip")
        self.root = self.path
        self.all = [x.replace(self.cmn, self.cmn + b".zip") for x in self.all]

    def test_sibling(self) -> None:
        """
        L{ZipPath.sibling} returns a path at the same level.
        """
        self.assertEqual(self.path.child("one").sibling("two"), self.path.child("two"))

    def test_zipPathRepr(self) -> None:
        """
        Make sure that invoking ZipPath's repr prints the correct class name
        and an absolute path to the zip file.
        """
        child: Union[ZipPath[str, bytes], ZipPath[str, str]] = self.path.child("foo")
        pathRepr = "ZipPath({!r})".format(
            os.path.abspath(self.nativecmn + ".zip" + os.sep + "foo"),
        )

        # Check for an absolute path
        self.assertEqual(repr(child), pathRepr)

        # Create a path to the file rooted in the current working directory
        relativeCommon = self.nativecmn.replace(os.getcwd() + os.sep, "", 1) + ".zip"
        relpath = ZipArchive(relativeCommon)
        child = relpath.child("foo")

        # Check using a path without the cwd prepended
        self.assertEqual(repr(child), pathRepr)

    def test_zipPathReprParentDirSegment(self) -> None:
        """
        The repr of a ZipPath with C{".."} in the internal part of its path
        includes the C{".."} rather than applying the usual parent directory
        meaning.
        """
        child = self.path.child("foo").child("..").child("bar")
        pathRepr = "ZipPath(%r)" % (
            self.nativecmn + ".zip" + os.sep.join(["", "foo", "..", "bar"])
        )
        self.assertEqual(repr(child), pathRepr)

    def test_zipArchiveRepr(self) -> None:
        """
        Make sure that invoking ZipArchive's repr prints the correct class
        name and an absolute path to the zip file.
        """
        path = ZipArchive(self.nativecmn + ".zip")
        pathRepr = "ZipArchive({!r})".format(os.path.abspath(self.nativecmn + ".zip"))

        # Check for an absolute path
        self.assertEqual(repr(path), pathRepr)

        # Create a path to the file rooted in the current working directory
        relativeCommon = self.nativecmn.replace(os.getcwd() + os.sep, "", 1) + ".zip"
        relpath = ZipArchive(relativeCommon)

        # Check using a path without the cwd prepended
        self.assertEqual(repr(relpath), pathRepr)
