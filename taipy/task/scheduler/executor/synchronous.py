__all__ = ["Synchronous"]

from concurrent.futures import Executor, Future


class Synchronous(Executor):
    """
    Equivalence of Python standard Thread/Process Pool Executor but
    the function is executed directly
    """

    @staticmethod
    def submit(fn, /, *args, **kwargs):
        future: Future = Future()
        future.set_result(fn(*args, **kwargs))
        return future
