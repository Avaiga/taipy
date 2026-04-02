import typing as t

from taipy.common.logger._taipy_logger import _TaipyLogger  # pyright: ignore[reportPrivateUsage]

logger = _TaipyLogger._get_logger()

class UpdateAware:

    __DEFAULT_EVENT_NAME = "default"
    __VAR_NAME = "_update_aware_instances"

    def __init__(self):
        self._update_aware = True

    def register_update_aware_listener(
        self, listener: t.Callable, event_name: str = __DEFAULT_EVENT_NAME, data: t.Optional[dict[str, t.Any]] = None
    ):
        """Registers an update aware instance to receive state updates.

        Args:
            update_aware: An instance of a class that is marked as update aware.
        """
        if not hasattr(self, self.__VAR_NAME):
            setattr(self, self.__VAR_NAME, {})
        instances = getattr(self, self.__VAR_NAME)
        if event_name not in instances:
            instances[event_name] = {}
        if listener in instances[event_name]:
            instances[event_name][listener].update(data or {})
        else:
            instances[event_name][listener] = data or {}

    def notify_update_aware_listeners(self, event_name: str = __DEFAULT_EVENT_NAME):
        """Notifies all registered update aware listeners of a state update.

        Args:
            event_name: The name of the event that triggered the update.
            state: The updated state to be passed to the listeners.
        """
        if hasattr(self, self.__VAR_NAME) and event_name in getattr(self, self.__VAR_NAME):
            instances = getattr(self, self.__VAR_NAME)
            for listener, data in instances[event_name].items():
                try:
                    listener(**data)
                except Exception as e:
                    logger.exception("Error notifying listener '%s':", listener, exc_info=e)
