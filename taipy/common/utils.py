from importlib import import_module


def load_fct(module_name, fct_name):
    module = import_module(module_name)
    return getattr(module, fct_name)


def objs_to_dict(objs):
    return [{"fct_name": obj.__name__, "fct_module": obj.__module__} for obj in objs]
