# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
HTTP errors.
"""

from __future__ import annotations

import re
import sys
import traceback

from twisted.python.compat import nativeString
from twisted.trial import unittest
from twisted.web import error
from twisted.web.template import Tag


class CodeToMessageTests(unittest.TestCase):
    """
    L{_codeToMessages} inverts L{_responses.RESPONSES}
    """

    def test_validCode(self) -> None:
        m = error._codeToMessage(b"302")
        self.assertEqual(m, b"Found")

    def test_invalidCode(self) -> None:
        m = error._codeToMessage(b"987")
        self.assertEqual(m, None)

    def test_nonintegerCode(self) -> None:
        m = error._codeToMessage(b"InvalidCode")
        self.assertEqual(m, None)


class ErrorTests(unittest.TestCase):
    """
    Tests for how L{Error} attributes are initialized.
    """

    def test_noMessageValidStatus(self) -> None:
        """
        If no C{message} argument is passed to the L{Error} constructor and the
        C{code} argument is a valid HTTP status code, C{message} is set to the
        HTTP reason phrase for C{code}.
        """
        e = error.Error(b"200")
        self.assertEqual(e.message, b"OK")
        self.assertEqual(str(e), "200 OK")

    def test_noMessageForStatus(self) -> None:
        """
        If no C{message} argument is passed to the L{Error} constructor and
        C{code} isn't a known HTTP status code, C{message} stays L{None}.
        """
        e = error.Error(b"999")
        self.assertEqual(e.message, None)
        self.assertEqual(str(e), "999")

    def test_invalidStatus(self) -> None:
        """
        If C{code} isn't plausibly an HTTP status code (i.e., composed of
        digits) it is rejected with L{ValueError}.
        """
        with self.assertRaises(ValueError):
            error.Error(b"InvalidStatus")

    def test_messageExists(self) -> None:
        """
        If a C{message} argument is passed to the L{Error} constructor, the
        C{message} isn't affected by the value of C{status}.
        """
        e = error.Error(b"200", b"My own message")
        self.assertEqual(e.message, b"My own message")
        self.assertEqual(str(e), "200 My own message")

    def test_str(self) -> None:
        """
        C{str()} on an L{Error} returns the code and message it was
        instantiated with.
        """
        # Bytestring status
        e = error.Error(b"200", b"OK")
        self.assertEqual(str(e), "200 OK")

        # int status
        e = error.Error(200, b"OK")
        self.assertEqual(str(e), "200 OK")


class PageRedirectTests(unittest.TestCase):
    """
    Tests for how L{PageRedirect} attributes are initialized.
    """

    def test_noMessageValidStatus(self) -> None:
        """
        If no C{message} argument is passed to the L{PageRedirect} constructor
        and the C{code} argument is a valid HTTP status code, C{code} is mapped
        to a descriptive string to which C{message} is assigned.
        """
        e = error.PageRedirect(b"200", location=b"/foo")
        self.assertEqual(e.message, b"OK to /foo")

    def test_noMessageValidStatusNoLocation(self) -> None:
        """
        If no C{message} argument is passed to the L{PageRedirect} constructor
        and C{location} is also empty and the C{code} argument is a valid HTTP
        status code, C{code} is mapped to a descriptive string to which
        C{message} is assigned without trying to include an empty location.
        """
        e = error.PageRedirect(b"200")
        self.assertEqual(e.message, b"OK")

    def test_noMessageInvalidStatusLocationExists(self) -> None:
        """
        If no C{message} argument is passed to the L{PageRedirect} constructor
        and C{code} isn't a valid HTTP status code, C{message} stays L{None}.
        """
        e = error.PageRedirect(b"999", location=b"/foo")
        self.assertEqual(e.message, None)

    def test_messageExistsLocationExists(self) -> None:
        """
        If a C{message} argument is passed to the L{PageRedirect} constructor,
        the C{message} isn't affected by the value of C{status}.
        """
        e = error.PageRedirect(b"200", b"My own message", location=b"/foo")
        self.assertEqual(e.message, b"My own message to /foo")

    def test_messageExistsNoLocation(self) -> None:
        """
        If a C{message} argument is passed to the L{PageRedirect} constructor
        and no location is provided, C{message} doesn't try to include the
        empty location.
        """
        e = error.PageRedirect(b"200", b"My own message")
        self.assertEqual(e.message, b"My own message")


class InfiniteRedirectionTests(unittest.TestCase):
    """
    Tests for how L{InfiniteRedirection} attributes are initialized.
    """

    def test_noMessageValidStatus(self) -> None:
        """
        If no C{message} argument is passed to the L{InfiniteRedirection}
        constructor and the C{code} argument is a valid HTTP status code,
        C{code} is mapped to a descriptive string to which C{message} is
        assigned.
        """
        e = error.InfiniteRedirection(b"200", location=b"/foo")
        self.assertEqual(e.message, b"OK to /foo")

    def test_noMessageValidStatusNoLocation(self) -> None:
        """
        If no C{message} argument is passed to the L{InfiniteRedirection}
        constructor and C{location} is also empty and the C{code} argument is a
        valid HTTP status code, C{code} is mapped to a descriptive string to
        which C{message} is assigned without trying to include an empty
        location.
        """
        e = error.InfiniteRedirection(b"200")
        self.assertEqual(e.message, b"OK")

    def test_noMessageInvalidStatusLocationExists(self) -> None:
        """
        If no C{message} argument is passed to the L{InfiniteRedirection}
        constructor and C{code} isn't a valid HTTP status code, C{message} stays
        L{None}.
        """
        e = error.InfiniteRedirection(b"999", location=b"/foo")
        self.assertEqual(e.message, None)
        self.assertEqual(str(e), "999")

    def test_messageExistsLocationExists(self) -> None:
        """
        If a C{message} argument is passed to the L{InfiniteRedirection}
        constructor, the C{message} isn't affected by the value of C{status}.
        """
        e = error.InfiniteRedirection(b"200", b"My own message", location=b"/foo")
        self.assertEqual(e.message, b"My own message to /foo")

    def test_messageExistsNoLocation(self) -> None:
        """
        If a C{message} argument is passed to the L{InfiniteRedirection}
        constructor and no location is provided, C{message} doesn't try to
        include the empty location.
        """
        e = error.InfiniteRedirection(b"200", b"My own message")
        self.assertEqual(e.message, b"My own message")


class RedirectWithNoLocationTests(unittest.TestCase):
    """
    L{RedirectWithNoLocation} is a subclass of L{Error} which sets
    a custom message in the constructor.
    """

    def test_validMessage(self) -> None:
        """
        When C{code}, C{message}, and C{uri} are passed to the
        L{RedirectWithNoLocation} constructor, the C{message} and C{uri}
        attributes are set, respectively.
        """
        e = error.RedirectWithNoLocation(b"302", b"REDIRECT", b"https://example.com")
        self.assertEqual(e.message, b"REDIRECT to https://example.com")
        self.assertEqual(e.uri, b"https://example.com")


class MissingRenderMethodTests(unittest.TestCase):
    """
    Tests for how L{MissingRenderMethod} exceptions are initialized and
    displayed.
    """

    def test_constructor(self) -> None:
        """
        Given C{element} and C{renderName} arguments, the
        L{MissingRenderMethod} constructor assigns the values to the
        corresponding attributes.
        """
        elt = object()
        e = error.MissingRenderMethod(elt, "renderThing")
        self.assertIs(e.element, elt)
        self.assertIs(e.renderName, "renderThing")

    def test_repr(self) -> None:
        """
        A L{MissingRenderMethod} is represented using a custom string
        containing the element's representation and the method name.
        """
        elt = object()
        e = error.MissingRenderMethod(elt, "renderThing")
        self.assertEqual(
            repr(e),
            ("'MissingRenderMethod': " "%r had no render method named 'renderThing'")
            % elt,
        )


class MissingTemplateLoaderTests(unittest.TestCase):
    """
    Tests for how L{MissingTemplateLoader} exceptions are initialized and
    displayed.
    """

    def test_constructor(self) -> None:
        """
        Given an C{element} argument, the L{MissingTemplateLoader} constructor
        assigns the value to the corresponding attribute.
        """
        elt = object()
        e = error.MissingTemplateLoader(elt)
        self.assertIs(e.element, elt)

    def test_repr(self) -> None:
        """
        A L{MissingTemplateLoader} is represented using a custom string
        containing the element's representation and the method name.
        """
        elt = object()
        e = error.MissingTemplateLoader(elt)
        self.assertEqual(repr(e), "'MissingTemplateLoader': %r had no loader" % elt)


class FlattenerErrorTests(unittest.TestCase):
    """
    Tests for L{FlattenerError}.
    """

    def makeFlattenerError(self, roots: list[object] = []) -> error.FlattenerError:
        try:
            raise RuntimeError("oh noes")
        except Exception as e:
            tb = traceback.extract_tb(sys.exc_info()[2])
            return error.FlattenerError(e, roots, tb)

    def fakeFormatRoot(self, obj: object) -> str:
        return "R(%s)" % obj

    def test_constructor(self) -> None:
        """
        Given C{exception}, C{roots}, and C{traceback} arguments, the
        L{FlattenerError} constructor assigns the roots to the C{_roots}
        attribute.
        """
        e = self.makeFlattenerError(roots=["a", "b"])
        self.assertEqual(e._roots, ["a", "b"])

    def test_str(self) -> None:
        """
        The string form of a L{FlattenerError} is identical to its
        representation.
        """
        e = self.makeFlattenerError()
        self.assertEqual(str(e), repr(e))

    def test_reprWithRootsAndWithTraceback(self) -> None:
        """
        The representation of a L{FlattenerError} initialized with roots and a
        traceback contains a formatted representation of those roots (using
        C{_formatRoot}) and a formatted traceback.
        """
        e = self.makeFlattenerError(["a", "b"])
        e._formatRoot = self.fakeFormatRoot  # type: ignore[method-assign]
        self.assertTrue(
            re.match(
                "Exception while flattening:\n"
                "  R\\(a\\)\n"
                "  R\\(b\\)\n"
                '  File "[^"]*", line [0-9]*, in makeFlattenerError\n'
                '    raise RuntimeError\\("oh noes"\\)\n'
                "RuntimeError: oh noes\n$",
                repr(e),
                re.M | re.S,
            ),
            repr(e),
        )

    def test_reprWithoutRootsAndWithTraceback(self) -> None:
        """
        The representation of a L{FlattenerError} initialized without roots but
        with a traceback contains a formatted traceback but no roots.
        """
        e = self.makeFlattenerError([])
        self.assertTrue(
            re.match(
                "Exception while flattening:\n"
                '  File "[^"]*", line [0-9]*, in makeFlattenerError\n'
                '    raise RuntimeError\\("oh noes"\\)\n'
                "RuntimeError: oh noes\n$",
                repr(e),
                re.M | re.S,
            ),
            repr(e),
        )

    def test_reprWithoutRootsAndWithoutTraceback(self) -> None:
        """
        The representation of a L{FlattenerError} initialized without roots but
        with a traceback contains a formatted traceback but no roots.
        """
        e = error.FlattenerError(RuntimeError("oh noes"), [], None)
        self.assertTrue(
            re.match(
                "Exception while flattening:\n" "RuntimeError: oh noes\n$",
                repr(e),
                re.M | re.S,
            ),
            repr(e),
        )

    def test_formatRootShortUnicodeString(self) -> None:
        """
        The C{_formatRoot} method formats a short unicode string using the
        built-in repr.
        """
        e = self.makeFlattenerError()
        self.assertEqual(e._formatRoot(nativeString("abcd")), repr("abcd"))

    def test_formatRootLongUnicodeString(self) -> None:
        """
        The C{_formatRoot} method formats a long unicode string using the
        built-in repr with an ellipsis.
        """
        e = self.makeFlattenerError()
        longString = nativeString("abcde-" * 20)
        self.assertEqual(
            e._formatRoot(longString),
            repr("abcde-abcde-abcde-ab<...>e-abcde-abcde-abcde-"),
        )

    def test_formatRootShortByteString(self) -> None:
        """
        The C{_formatRoot} method formats a short byte string using the
        built-in repr.
        """
        e = self.makeFlattenerError()
        self.assertEqual(e._formatRoot(b"abcd"), repr(b"abcd"))

    def test_formatRootLongByteString(self) -> None:
        """
        The C{_formatRoot} method formats a long byte string using the
        built-in repr with an ellipsis.
        """
        e = self.makeFlattenerError()
        longString = b"abcde-" * 20
        self.assertEqual(
            e._formatRoot(longString),
            repr(b"abcde-abcde-abcde-ab<...>e-abcde-abcde-abcde-"),
        )

    def test_formatRootTagNoFilename(self) -> None:
        """
        The C{_formatRoot} method formats a C{Tag} with no filename information
        as 'Tag <tagName>'.
        """
        e = self.makeFlattenerError()
        self.assertEqual(e._formatRoot(Tag("a-tag")), "Tag <a-tag>")

    def test_formatRootTagWithFilename(self) -> None:
        """
        The C{_formatRoot} method formats a C{Tag} with filename information
        using the filename, line, column, and tag information
        """
        e = self.makeFlattenerError()
        t = Tag("a-tag", filename="tpl.py", lineNumber=10, columnNumber=20)
        self.assertEqual(
            e._formatRoot(t), 'File "tpl.py", line 10, column 20, in "a-tag"'
        )

    def test_string(self) -> None:
        """
        If a L{FlattenerError} is created with a string root, up to around 40
        bytes from that string are included in the string representation of the
        exception.
        """
        self.assertEqual(
            str(error.FlattenerError(RuntimeError("reason"), ["abc123xyz"], [])),
            "Exception while flattening:\n" "  'abc123xyz'\n" "RuntimeError: reason\n",
        )
        self.assertEqual(
            str(error.FlattenerError(RuntimeError("reason"), ["0123456789" * 10], [])),
            "Exception while flattening:\n"
            "  '01234567890123456789"
            "<...>01234567890123456789'\n"  # TODO: re-add 0
            "RuntimeError: reason\n",
        )

    def test_unicode(self) -> None:
        """
        If a L{FlattenerError} is created with a unicode root, up to around 40
        characters from that string are included in the string representation
        of the exception.
        """
        self.assertEqual(
            str(
                error.FlattenerError(RuntimeError("reason"), ["abc\N{SNOWMAN}xyz"], [])
            ),
            "Exception while flattening:\n"
            "  'abc\\u2603xyz'\n"  # Codepoint for SNOWMAN
            "RuntimeError: reason\n",
        )
        self.assertEqual(
            str(
                error.FlattenerError(
                    RuntimeError("reason"), ["01234567\N{SNOWMAN}9" * 10], []
                )
            ),
            "Exception while flattening:\n"
            "  '01234567\\u2603901234567\\u26039"
            "<...>01234567\\u2603901234567"
            "\\u26039'\n"
            "RuntimeError: reason\n",
        )


class UnsupportedMethodTests(unittest.SynchronousTestCase):
    """
    Tests for L{UnsupportedMethod}.
    """

    def test_str(self) -> None:
        """
        The C{__str__} for L{UnsupportedMethod} makes it clear that what it
        shows is a list of the supported methods, not the method that was
        unsupported.
        """
        e = error.UnsupportedMethod([b"HEAD", b"PATCH"])
        self.assertEqual(
            str(e),
            "Expected one of [b'HEAD', b'PATCH']",
        )
