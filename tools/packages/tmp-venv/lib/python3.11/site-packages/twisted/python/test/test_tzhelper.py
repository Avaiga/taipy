# # Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python._tzhelper}.
"""

from __future__ import annotations

from os import environ

try:
    from time import tzset as _tzset
except ImportError:
    tzset = None
else:
    tzset = _tzset

from datetime import datetime, timedelta
from time import mktime as mktime_real

from twisted.python._tzhelper import FixedOffsetTimeZone
from twisted.trial.unittest import SkipTest, TestCase

# On some rare platforms (FreeBSD 8?  I was not able to reproduce
# on FreeBSD 9) 'mktime' seems to always fail once tzset() has been
# called more than once in a process lifetime.  I think this is
# just a platform bug, so let's work around it.  -glyph


def mktime(t9: tuple[int, int, int, int, int, int, int, int, int]) -> float:
    """
    Call L{mktime_real}, and if it raises L{OverflowError}, catch it and raise
    SkipTest instead.

    @param t9: A time as a 9-item tuple.
    @type t9: L{tuple}

    @return: A timestamp.
    @rtype: L{float}
    """
    try:
        return mktime_real(t9)
    except OverflowError:
        raise SkipTest(f"Platform cannot construct time zone for {t9!r}")


def setTZ(name: str | None) -> None:
    """
    Set time zone.

    @param name: a time zone name
    @type name: L{str}
    """
    if tzset is None:
        return

    if name is None:
        try:
            del environ["TZ"]
        except KeyError:
            pass
    else:
        environ["TZ"] = name
    tzset()


def addTZCleanup(testCase: TestCase) -> None:
    """
    Add cleanup hooks to a test case to reset timezone to original value.

    @param testCase: the test case to add the cleanup to.
    @type testCase: L{unittest.TestCase}
    """
    tzIn = environ.get("TZ", None)

    @testCase.addCleanup
    def resetTZ() -> None:
        setTZ(tzIn)


class FixedOffsetTimeZoneTests(TestCase):
    """
    Tests for L{FixedOffsetTimeZone}.
    """

    def test_tzinfo(self) -> None:
        """
        Test that timezone attributes respect the timezone as set by the
        standard C{TZ} environment variable and L{tzset} API.
        """
        if tzset is None:
            raise SkipTest("Platform cannot change timezone; unable to verify offsets.")

        def testForTimeZone(
            name: str, expectedOffsetDST: str, expectedOffsetSTD: str
        ) -> None:
            setTZ(name)

            localDST = mktime((2006, 6, 30, 0, 0, 0, 4, 181, 1))
            localDSTdt = datetime.fromtimestamp(localDST)
            localSTD = mktime((2007, 1, 31, 0, 0, 0, 2, 31, 0))
            localSTDdt = datetime.fromtimestamp(localSTD)

            tzDST = FixedOffsetTimeZone.fromLocalTimeStamp(localDST)
            tzSTD = FixedOffsetTimeZone.fromLocalTimeStamp(localSTD)

            self.assertEqual(tzDST.tzname(localDSTdt), f"UTC{expectedOffsetDST}")
            self.assertEqual(tzSTD.tzname(localSTDdt), f"UTC{expectedOffsetSTD}")

            self.assertEqual(tzDST.dst(localDSTdt), timedelta(0))
            self.assertEqual(tzSTD.dst(localSTDdt), timedelta(0))

            def timeDeltaFromOffset(offset: str) -> timedelta:
                assert len(offset) == 5

                sign = offset[0]
                hours = int(offset[1:3])
                minutes = int(offset[3:5])

                if sign == "-":
                    hours = -hours
                    minutes = -minutes
                else:
                    assert sign == "+"

                return timedelta(hours=hours, minutes=minutes)

            self.assertEqual(
                tzDST.utcoffset(localDSTdt), timeDeltaFromOffset(expectedOffsetDST)
            )
            self.assertEqual(
                tzSTD.utcoffset(localSTDdt), timeDeltaFromOffset(expectedOffsetSTD)
            )

        addTZCleanup(self)

        # UTC
        testForTimeZone("UTC+00", "+0000", "+0000")
        # West of UTC
        testForTimeZone("EST+05EDT,M4.1.0,M10.5.0", "-0400", "-0500")
        # East of UTC
        testForTimeZone("CEST-01CEDT,M4.1.0,M10.5.0", "+0200", "+0100")
        # No DST
        testForTimeZone("CST+06", "-0600", "-0600")
