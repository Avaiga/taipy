import threading
import typing as t
from werkzeug.local import Local, release_local

class _ContextForState(object):

    def __init__(self) -> None:
        self.__data = Local()

    def __enter__(self):
        print(f"Context.Enter {threading.currentThread().getName()}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        release_local(self.__data)
        print(f"Context.Exit in {threading.currentThread().getName()}")

    def get_client_id(self) -> t.Optional[str]:
        return getattr(self.__data, "client_id")

    def set_client_id(self, client_id: str):
        self.__data.client_id = client_id
        print(f"Context.set_client_id in {threading.currentThread().getName()}")
