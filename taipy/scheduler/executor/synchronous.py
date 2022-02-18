__all__ = ["Synchronous"]

from concurrent.futures import Executor, Future


class Synchronous(Executor):
    """Equivalent to the Python standard Thread/Process Pool Executor but
    the function is executed directly.
    """

    @staticmethod
    def submit(fn, /, *args, **kwargs):
        future: Future = Future()

        try:
            future.set_result(fn(*args, **kwargs))
        except Exception as e:
            future.set_exception(e)

        return future
