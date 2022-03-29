import datetime
import os
from unittest import mock

import pytest

from taipy.core import Frequency
from taipy.core.common.scope import Scope
from taipy.core.config._config_template_handler import _ConfigTemplateHandler
from taipy.core.exceptions.exceptions import InconsistentEnvVariableError


def test_replace_if_template():
    assert_does_not_change("123")
    assert_does_not_change("foo")
    assert_does_not_change("_foo")
    assert_does_not_change("_foo_")
    assert_does_not_change("foo_")
    assert_does_not_change("foo")
    assert_does_not_change("foo_1")
    assert_does_not_change("1foo_1")
    assert_does_not_change("env(foo)")
    assert_does_not_change("env<foo>")
    assert_does_not_change("env[foo]")
    assert_does_not_change("Env[foo]")
    assert_does_not_change("ENV[1foo]")

    assert_does_not_change("123:bool")
    assert_does_not_change("foo:bool")
    assert_does_not_change("_foo:bool")
    assert_does_not_change("_foo_:bool")
    assert_does_not_change("foo_:bool")
    assert_does_not_change("foo:bool")
    assert_does_not_change("foo_1:bool")
    assert_does_not_change("1foo_1:bool")
    assert_does_not_change("env(foo):bool")
    assert_does_not_change("env<foo>:bool")
    assert_does_not_change("env[foo]:bool")
    assert_does_not_change("Env[foo]:bool")
    assert_does_not_change("ENV[1foo]:bool")

    assert_does_not_change("ENV[foo]:")
    assert_does_not_change("ENV[_foo]:")
    assert_does_not_change("ENV[foo_]:")
    assert_does_not_change("ENV[foo0]:")
    assert_does_not_change("ENV[foo_0]:")
    assert_does_not_change("ENV[_foo_0]:")

    assert_does_not_change("ENV[foo]:foo")
    assert_does_not_change("ENV[_foo]:foo")
    assert_does_not_change("ENV[foo_]:foo")
    assert_does_not_change("ENV[foo0]:foo")
    assert_does_not_change("ENV[foo_0]:foo")
    assert_does_not_change("ENV[_foo_0]:foo")

    assert_does_replace("ENV[foo]", "foo", "VALUE", str)
    assert_does_replace("ENV[_foo]", "_foo", "VALUE", str)
    assert_does_replace("ENV[foo_]", "foo_", "VALUE", str)
    assert_does_replace("ENV[foo0]", "foo0", "VALUE", str)
    assert_does_replace("ENV[foo_0]", "foo_0", "VALUE", str)
    assert_does_replace("ENV[_foo_0]", "_foo_0", "VALUE", str)

    assert_does_replace("ENV[foo]:str", "foo", "VALUE", str)
    assert_does_replace("ENV[_foo]:str", "_foo", "VALUE", str)
    assert_does_replace("ENV[foo_]:str", "foo_", "VALUE", str)
    assert_does_replace("ENV[foo0]:str", "foo0", "VALUE", str)
    assert_does_replace("ENV[foo_0]:str", "foo_0", "VALUE", str)
    assert_does_replace("ENV[_foo_0]:str", "_foo_0", "VALUE", str)

    assert_does_replace("ENV[foo]:int", "foo", "1", int)
    assert_does_replace("ENV[_foo]:int", "_foo", "1", int)
    assert_does_replace("ENV[foo_]:int", "foo_", "1", int)
    assert_does_replace("ENV[foo0]:int", "foo0", "1", int)
    assert_does_replace("ENV[foo_0]:int", "foo_0", "1", int)
    assert_does_replace("ENV[_foo_0]:int", "_foo_0", "1", int)

    assert_does_replace("ENV[foo]:float", "foo", "1.", float)
    assert_does_replace("ENV[_foo]:float", "_foo", "1.", float)
    assert_does_replace("ENV[foo_]:float", "foo_", "1.", float)
    assert_does_replace("ENV[foo0]:float", "foo0", "1.", float)
    assert_does_replace("ENV[foo_0]:float", "foo_0", "1.", float)
    assert_does_replace("ENV[_foo_0]:float", "_foo_0", "1.", float)

    assert_does_replace("ENV[foo]:bool", "foo", "True", bool)
    assert_does_replace("ENV[_foo]:bool", "_foo", "True", bool)
    assert_does_replace("ENV[foo_]:bool", "foo_", "True", bool)
    assert_does_replace("ENV[foo0]:bool", "foo0", "True", bool)
    assert_does_replace("ENV[foo_0]:bool", "foo_0", "True", bool)
    assert_does_replace("ENV[_foo_0]:bool", "_foo_0", "True", bool)


def assert_does_replace(template, env_variable_name, replaced_by, as_type):
    with mock.patch.dict(os.environ, {env_variable_name: replaced_by}):
        tpl = _ConfigTemplateHandler()
        assert tpl._replace_templates(template) == as_type(replaced_by)


def assert_does_not_change(template):
    tpl = _ConfigTemplateHandler()
    assert tpl._replace_templates(template) == template


def test_replace_tuple_list_dict():
    with mock.patch.dict(os.environ, {"FOO": "true", "BAR": "3", "BAZ": "qux"}):
        tpl = _ConfigTemplateHandler()
        now = datetime.datetime.now()
        actual = tpl._replace_templates(("ENV[FOO]:bool", now, "ENV[BAR]:int", "ENV[BAZ]", "quz"))
        assert actual == (True, now, 3, "qux", "quz")
        actual = tpl._replace_templates(("ENV[FOO]:bool", now, "ENV[BAR]:int", "ENV[BAZ]", "quz"))
        assert actual == (True, now, 3, "qux", "quz")


def test_to_bool():
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_bool("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_bool("no")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_bool("tru")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_bool("tru_e")

    assert _ConfigTemplateHandler._to_bool("true")
    assert _ConfigTemplateHandler._to_bool("True")
    assert _ConfigTemplateHandler._to_bool("TRUE")
    assert _ConfigTemplateHandler._to_bool("TruE")
    assert _ConfigTemplateHandler._to_bool("TrUE")

    assert not _ConfigTemplateHandler._to_bool("false")
    assert not _ConfigTemplateHandler._to_bool("False")
    assert not _ConfigTemplateHandler._to_bool("FALSE")
    assert not _ConfigTemplateHandler._to_bool("FalSE")
    assert not _ConfigTemplateHandler._to_bool("FalSe")


def test_to_int():
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_int("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_int("_45")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_int("12.5")

    assert 12 == _ConfigTemplateHandler._to_int("12")
    assert 0 == _ConfigTemplateHandler._to_int("0")
    assert -2 == _ConfigTemplateHandler._to_int("-2")
    assert 156165 == _ConfigTemplateHandler._to_int("156165")


def test_to_float():
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_float("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_float("_45")

    assert 12.5 == _ConfigTemplateHandler._to_float("12.5")
    assert 2.0 == _ConfigTemplateHandler._to_float("2")
    assert 0.0 == _ConfigTemplateHandler._to_float("0")
    assert -2.1 == _ConfigTemplateHandler._to_float("-2.1")
    assert 156165.3 == _ConfigTemplateHandler._to_float("156165.3")


def test_to_scope():
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_scope("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_scope("plop")

    assert Scope.PIPELINE == _ConfigTemplateHandler._to_scope("pipeline")
    assert Scope.PIPELINE == _ConfigTemplateHandler._to_scope("PIPELINE")
    assert Scope.SCENARIO == _ConfigTemplateHandler._to_scope("SCENARIO")
    assert Scope.CYCLE == _ConfigTemplateHandler._to_scope("cycle")


def test_to_frequency():
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_frequency("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _ConfigTemplateHandler._to_frequency("plop")

    assert Frequency.DAILY == _ConfigTemplateHandler._to_frequency("DAILY")
    assert Frequency.DAILY == _ConfigTemplateHandler._to_frequency("Daily")
    assert Frequency.WEEKLY == _ConfigTemplateHandler._to_frequency("weekly")
    assert Frequency.WEEKLY == _ConfigTemplateHandler._to_frequency("WEEKLY")
    assert Frequency.MONTHLY == _ConfigTemplateHandler._to_frequency("Monthly")
    assert Frequency.MONTHLY == _ConfigTemplateHandler._to_frequency("MONThLY")
    assert Frequency.QUARTERLY == _ConfigTemplateHandler._to_frequency("QuaRtERlY")
    assert Frequency.YEARLY == _ConfigTemplateHandler._to_frequency("Yearly")
