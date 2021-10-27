import multiprocessing

from taipy.data import DataSource


class LockDataSource(DataSource):
    def __init__(self, name, lock, **kwargs):
        super().__init__(name, **kwargs)
        self._lock = lock
        self._lock.acquire()

    def get(self, query=None):
        with self._lock:
            return None

    def write(self, data):
        print("write-------------------", flush=True)
        self._lock.release()
