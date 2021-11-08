__all__ = ["RemotePoolExecutor"]

from concurrent.futures import ThreadPoolExecutor
from importlib import import_module

from celery import Celery


class RemotePoolExecutor(ThreadPoolExecutor):
    """
    Equivalence of Python standard Thread/Process Pool Executor but
    the function is executed through a Celery
    """

    def __init__(self, max_number_of_worker, *args, **kwargs):
        super().__init__(max_number_of_worker, *args, **kwargs)
        self.app = Celery("tasks", backend="rpc://", broker="pyamqp://guest@rabbitmq//")
        self.remote_executor = self.app.task(self._execute)

    def submit(self, fn, /, *args, **kwargs):
        to_execute = self.remote_executor.delay(fn.__module__, fn.__name__, *args, **kwargs)
        return super().submit(to_execute.get)

    def as_worker(self):
        self.app.worker_main(argv=["worker", "--loglevel=info"])

    @staticmethod
    def _execute(module_name, fct_name, *args, **kwargs):
        module = import_module(module_name)
        fct = getattr(module, fct_name)
        return fct(*args, **kwargs)
