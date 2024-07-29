import typing as t

from taipy.logger._taipy_logger import _TaipyLogger

from .utils.singleton import _Singleton


class BaseGuiHook:
    exposed_hooks: t.List[str] = []


class GuiHooks(object, metaclass=_Singleton):
    def __init__(self):
        self.__hooks: t.List[BaseGuiHook] = []

    def _register_gui_hook(self, hook: BaseGuiHook):
        self.__hooks.append(hook)

    def __getattr__(self, name: str):
        def _resolve_hook(*args, **kwargs):
            for hook in self.__hooks:
                if name not in hook.exposed_hooks:
                    continue
                # call hook
                try:
                    res = getattr(hook, name)(*args, **kwargs)
                except Exception as e:
                    _TaipyLogger._get_logger().error(f"Error while calling Gui Hooks '{name}': {e}")
                    return
                # check if the hook returns True -> stop the chain
                if res == True:
                    return
                # only hooks that return true are allowed to return values to ensure consistent response
                if isinstance(res, (list, tuple)) and len(res) == 2 and res[0] == True:
                    return res[1] or None

        return _resolve_hook
