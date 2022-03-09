import warnings

import pytest

from taipy.gui.utils.date import _ISO_to_date
from taipy.gui.utils.types import _TaipyBase, _TaipyBool, _TaipyDate, _TaipyNumber


def test_taipy_base():
    tb = _TaipyBase("value", "hash")
    assert tb.get() == "value"
    assert tb.get_name() == "hash"
    tb.set("a value")
    assert tb.get() == "a value"
    assert tb.get_hash() == "TaipyBase"


def test_taipy_bool():
    assert _TaipyBool(0, "v").get() == False
    assert _TaipyBool(1, "v").get() == True
    assert _TaipyBool(False, "v").get() == False
    assert _TaipyBool(True, "v").get() == True
    assert _TaipyBool("", "v").get() == False
    assert _TaipyBool("hey", "v").get() == True
    assert _TaipyBool([], "v").get() == False
    assert _TaipyBool(["an item"], "v").get() == True


def test_taipy_number():
    with pytest.raises(ValueError):
        _TaipyNumber("a string", "x").get()
    with warnings.catch_warnings(record=True) as r:
        _TaipyNumber("a string", "x").cast_value("a string")
    _TaipyNumber(0, "x").cast_value(0)


def test_taipy_date():
    assert _TaipyDate(_ISO_to_date("2022-03-03 00:00:00 UTC"), "x").get() == "2022-03-03T00:00:00+00:00"
    assert _TaipyDate("2022-03-03 00:00:00 UTC", "x").get() == "2022-03-03 00:00:00 UTC"
    assert _TaipyDate(None, "x").get() is None
    _TaipyDate("", "x").cast_value("2022-03-03 00:00:00 UTC")
    _TaipyDate("", "x").cast_value(_ISO_to_date("2022-03-03 00:00:00 UTC"))
