from taipy.core.common._reload import set_entity


class _Entity:
    MANAGER_NAME: str
    _is_in_context = False

    def __enter__(self):
        self._is_in_context = True
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._is_in_context = False
        set_entity(self.MANAGER_NAME, self)
