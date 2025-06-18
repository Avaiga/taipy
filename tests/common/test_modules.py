import pytest

from taipy.common._modules import _assert_module_installation, _module_exists


def test_unknown_module():
    assert not _module_exists("unknown.module")


def test_known_module():
    assert _module_exists("taipy.common")


def test_dependency_installation():
    with pytest.raises(RuntimeError) as e:
        _assert_module_installation("taipy_test", "unknown_package", "unknown", "taipy_test")
    assert "pip install taipy_test[unknown]" in str(e.value)
