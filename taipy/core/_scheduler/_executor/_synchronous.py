from concurrent.futures import Executor, Future


class _Synchronous(Executor):
    """
    Similar to the Python standard Thread/Process Pool Executor but the function is executed directly in a
    synchronous mode.
    """

    @staticmethod
    def submit(fn, /, *args, **kwargs):
        """Execute the function submitted in a synchronous mode."""
        future: Future = Future()

        try:
            future.set_result(fn(*args, **kwargs))
        except Exception as e:
            future.set_exception(e)

        return future
