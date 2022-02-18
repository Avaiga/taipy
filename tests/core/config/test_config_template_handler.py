import os
from unittest import mock

import pytest

from taipy.core.config.config_template_handler import ConfigTemplateHandler
from taipy.core.data.scope import Scope
from taipy.core.exceptions.configuration import InconsistentEnvVariableError


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

    assert_does_replace("ENV[foo]", "foo")
    assert_does_replace("ENV[_foo]", "_foo")
    assert_does_replace("ENV[foo_]", "foo_")
    assert_does_replace("ENV[foo0]", "foo0")
    assert_does_replace("ENV[foo_0]", "foo_0")
    assert_does_replace("ENV[_foo_0]", "_foo_0")


def assert_does_replace(template, env_variable_name):
    with mock.patch.dict(os.environ, {env_variable_name: "VALUE"}):
        fact = ConfigTemplateHandler()
        assert fact.replace_templates(template) == "VALUE"


def assert_does_not_change(template):
    fact = ConfigTemplateHandler()
    assert fact.replace_templates(template) == template


def test_to_bool():
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_bool("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_bool("no")
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_bool("tru")
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_bool("tru_e")

    assert ConfigTemplateHandler.to_bool("true")
    assert ConfigTemplateHandler.to_bool("True")
    assert ConfigTemplateHandler.to_bool("TRUE")
    assert ConfigTemplateHandler.to_bool("TruE")
    assert ConfigTemplateHandler.to_bool("TrUE")

    assert not ConfigTemplateHandler.to_bool("false")
    assert not ConfigTemplateHandler.to_bool("False")
    assert not ConfigTemplateHandler.to_bool("FALSE")
    assert not ConfigTemplateHandler.to_bool("FalSE")
    assert not ConfigTemplateHandler.to_bool("FalSe")


def test_to_int():
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_int("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_int("_45")

    assert 12 == ConfigTemplateHandler.to_int("12")
    assert 0 == ConfigTemplateHandler.to_int("0")
    assert -2 == ConfigTemplateHandler.to_int("-2")
    assert 156165 == ConfigTemplateHandler.to_int("156165")


def test_to_scope():
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_scope("okhds")
    with pytest.raises(InconsistentEnvVariableError):
        ConfigTemplateHandler.to_scope("plop")

    assert Scope.PIPELINE == ConfigTemplateHandler.to_scope("pipeline")
    assert Scope.PIPELINE == ConfigTemplateHandler.to_scope("PIPELINE")
    assert Scope.SCENARIO == ConfigTemplateHandler.to_scope("SCENARIO")
    assert Scope.CYCLE == ConfigTemplateHandler.to_scope("cycle")
