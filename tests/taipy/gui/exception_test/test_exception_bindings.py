import pytest

from taipy.gui.utils._bindings import _Bindings


def test_exception_binding_twice(gui):
    bind = _Bindings(gui)
    bind._new_scopes()
    bind._bind("x", 10)
    with pytest.raises(ValueError):
        bind._bind("x", 10)


def test_exception_binding_invalid_name(gui):
    bind = _Bindings(gui)
    bind._new_scopes()
    with pytest.raises(ValueError):
        bind._bind("invalid identifier", 10)
