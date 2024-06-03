# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import datetime
import os
from unittest import mock

import pytest

from taipy.config.common._template_handler import _TemplateHandler
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.exceptions.exceptions import InconsistentEnvVariableError


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
        tpl = _TemplateHandler()
        assert tpl._replace_templates(template) == as_type(replaced_by)


def assert_does_not_change(template):
    tpl = _TemplateHandler()
    assert tpl._replace_templates(template) == template


def test_replace_tuple_list_dict():
    with mock.patch.dict(os.environ, {"FOO": "true", "BAR": "3", "BAZ": "qux"}):
        tpl = _TemplateHandler()
        now = datetime.datetime.now()
        actual = tpl._replace_templates(("ENV[FOO]:bool", now, "ENV[BAR]:int", "ENV[BAZ]", "quz"))
        assert actual == (True, now, 3, "qux", "quz")
        actual = tpl._replace_templates(("ENV[FOO]:bool", now, "ENV[BAR]:int", "ENV[BAZ]", "quz"))
        assert actual == (True, now, 3, "qux", "quz")


def test_to_bool():
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_bool("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_bool("no")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_bool("tru") # codespell:ignore tru
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_bool("tru_e")

    assert _TemplateHandler._to_bool("true")
    assert _TemplateHandler._to_bool("True")
    assert _TemplateHandler._to_bool("TRUE")
    assert _TemplateHandler._to_bool("TruE")
    assert _TemplateHandler._to_bool("TrUE")

    assert not _TemplateHandler._to_bool("false")
    assert not _TemplateHandler._to_bool("False")
    assert not _TemplateHandler._to_bool("FALSE")
    assert not _TemplateHandler._to_bool("FalSE")
    assert not _TemplateHandler._to_bool("FalSe")


def test_to_int():
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_int("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_int("_45")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_int("12.5")

    assert 12 == _TemplateHandler._to_int("12")
    assert 0 == _TemplateHandler._to_int("0")
    assert -2 == _TemplateHandler._to_int("-2")
    assert 156165 == _TemplateHandler._to_int("156165")


def test_to_float():
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_float("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_float("_45")

    assert 12.5 == _TemplateHandler._to_float("12.5")
    assert 2.0 == _TemplateHandler._to_float("2")
    assert 0.0 == _TemplateHandler._to_float("0")
    assert -2.1 == _TemplateHandler._to_float("-2.1")
    assert 156165.3 == _TemplateHandler._to_float("156165.3")


def test_to_scope():
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_scope("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_scope("plop")

    assert Scope.GLOBAL == _TemplateHandler._to_scope("global")
    assert Scope.GLOBAL == _TemplateHandler._to_scope("GLOBAL")
    assert Scope.SCENARIO == _TemplateHandler._to_scope("SCENARIO")
    assert Scope.CYCLE == _TemplateHandler._to_scope("cycle")


def test_to_frequency():
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_frequency("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        _TemplateHandler._to_frequency("plop")

    assert Frequency.DAILY == _TemplateHandler._to_frequency("DAILY")
    assert Frequency.DAILY == _TemplateHandler._to_frequency("Daily")
    assert Frequency.WEEKLY == _TemplateHandler._to_frequency("weekly")
    assert Frequency.WEEKLY == _TemplateHandler._to_frequency("WEEKLY")
    assert Frequency.MONTHLY == _TemplateHandler._to_frequency("Monthly")
    assert Frequency.MONTHLY == _TemplateHandler._to_frequency("MONThLY")
    assert Frequency.QUARTERLY == _TemplateHandler._to_frequency("QuaRtERlY")
    assert Frequency.YEARLY == _TemplateHandler._to_frequency("Yearly")
