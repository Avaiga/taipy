from importlib import import_module
from typing import Callable


def _load_fct(module_name: str, fct_name: str) -> Callable:
    module = import_module(module_name)
    return getattr(module, fct_name)


def _fct_to_dict(obj):
    return {"fct_name": obj.__name__, "fct_module": obj.__module__}


def _fcts_to_dict(objs):
    return [_fct_to_dict(obj) for obj in objs]
