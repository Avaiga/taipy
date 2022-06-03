import threading
import inspect

taipy_local_data = threading.local()

class _LockByClientId(object):

    def __init__(self) -> None:
        pass

    def __enter__(self):
        print(f"Lock.Enter {threading.currentThread().getName()}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        taipy_local_data.client_id = ""
        print(f"Lock.Exit in {threading.currentThread().getName()}")

    def set_client_id(self, client_id: str):
        taipy_local_data.client_id = client_id
        print(f"Lock.set_client_id in {threading.currentThread().getName()}")

    def get_client_id(self) -> str:
        return taipy_local_data.client_id