__all__ = ["RemotePoolExecutor"]

from concurrent.futures import ThreadPoolExecutor
from importlib import import_module

try:
    from celery import Celery
except ImportError:
    _has_celery = False
else:
    _has_celery = True


class RemotePoolExecutor(ThreadPoolExecutor):
    """Interface for dealing with remote worker through Celery.

    Equivalent to the Python standard Thread/Process Pool Executor but
    the function is executed through Celery. You should consider having the `celery` package
    installed with `rabbitmq`.
    Rabbitmq broker will be the bus between applications that will use the `submit` function to
    execute code on workers that will be waiting through the function `as_worker`.

    Attributes:
        app: Celery application for interaction with broker.
        remote_executor: Remote function that will execute code on workers.
    """

    def __init__(self, max_number_of_worker, hostname, *args, **kwargs):
        if not _has_celery:
            raise ImportError("celery is required.\nRun: pip install taipy[celery]")
        super().__init__(max_number_of_worker, *args, **kwargs)
        self.app = Celery("tasks", backend="rpc://", broker=f"pyamqp://guest@{hostname}//")
        self.remote_executor = self.app.task(self._execute)

    def submit(self, fn, /, *args, **kwargs):
        """Submit a function for executions.

        Returns:
            Future with the result of the execution.
        """
        to_execute = self.remote_executor.delay(fn.__module__, fn.__name__, *args, **kwargs)
        return super().submit(to_execute.get)

    def as_worker(self):
        """Worker mode of this executor.

        To be able to execute code, we should start worker that will grab tasks from Celery
        and execute them.
        This function should be executed as entrypoint of worker.
        """
        self.app.worker_main(argv=["worker", "--loglevel=info"])

    @staticmethod
    def _execute(module_name, fct_name, *args, **kwargs):
        module = import_module(module_name)
        fct = getattr(module, fct_name)
        return fct(*args, **kwargs)
