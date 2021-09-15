__all__ = ["FutureExecutor"]

from concurrent import futures
from concurrent.futures import Future


class FutureExecutor:
    """
    Equivalence of Python standard Thread/Process Pool Executor but the function is executed directly
    """

    @staticmethod
    def submit(fn, /, *args, **kwargs) -> futures:
        future = Future()
        future.set_result(fn(*args, **kwargs))
        return future

    @staticmethod
    def map(func, *iterables, timeout=None, chunksize=1):
        raise NotImplementedError

    @staticmethod
    def shutdown(wait=True, *, cancel_futures=False):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
