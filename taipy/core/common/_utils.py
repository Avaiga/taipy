import functools
from importlib import import_module
from operator import attrgetter
from typing import Callable, Optional


@functools.lru_cache
def _load_fct(module_name: str, fct_name: str) -> Callable:
    module = import_module(module_name)
    return attrgetter(fct_name)(module)


@functools.lru_cache
def _get_fct_name(f) -> Optional[str]:
    # Mock function does not have __qualname__ attribute -> return __name__
    # Partial or anonymous function does not have __name__ or __qualname__ attribute -> return None
    name = getattr(f, "__qualname__", getattr(f, "__name__", None))
    return name


def _fct_to_dict(obj):
    fct_name = _get_fct_name(obj)
    if not fct_name:
        return None
    return {"fct_name": fct_name, "fct_module": obj.__module__}


def _fcts_to_dict(objs):
    return [d for obj in objs if (d := _fct_to_dict(obj)) is not None]
