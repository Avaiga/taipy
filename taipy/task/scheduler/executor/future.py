__all__ = ["FutureExecutor"]

from concurrent.futures import Future, Executor


class FutureExecutor(Executor):
    """
    Equivalence of Python standard Thread/Process Pool Executor but the function is executed directly
    """

    @staticmethod
    def submit(fn, /, *args, **kwargs) -> Future:
        future: Future = Future()
        future.set_result(fn(*args, **kwargs))
        return future
