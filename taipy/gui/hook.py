import typing as t

from taipy.logger._taipy_logger import _TaipyLogger

from .utils.singleton import _Singleton


class Hook:
    method_names: t.List[str] = []


class Hooks(object, metaclass=_Singleton):
    def __init__(self):
        self.__hooks: t.List[Hook] = []

    def _register_hook(self, hook: Hook):
        # Prevent duplicated hooks
        for h in self.__hooks:
            if type(hook) is type(h):
                _TaipyLogger._get_logger().info(f"Failed to register duplicated hook of type '{type(h)}'")
                return
        self.__hooks.append(hook)

    def __getattr__(self, name: str):
        def _resolve_hook(*args, **kwargs):
            for hook in self.__hooks:
                if name not in hook.method_names:
                    continue
                # call hook
                try:
                    func = getattr(hook, name)
                    if not callable(func):
                        raise Exception(f"'{name}' hook is not callable")
                    res = getattr(hook, name)(*args, **kwargs)
                except Exception as e:
                    _TaipyLogger._get_logger().error(f"Error while calling hook '{name}': {e}")
                    return
                # check if the hook returns True -> stop the chain
                if res is True:
                    return
                # only hooks that return true are allowed to return values to ensure consistent response
                if isinstance(res, (list, tuple)) and len(res) == 2 and res[0] is True:
                    return res[1]

        return _resolve_hook
