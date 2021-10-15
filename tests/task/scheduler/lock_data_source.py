import multiprocessing

from taipy.data import DataSource


class LockDataSource(DataSource):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self._lock = multiprocessing.Lock()
        self._lock.acquire()

    def get(self, query=None):
        with self._lock:
            return None

    def write(self, data):
        self._lock.release()
