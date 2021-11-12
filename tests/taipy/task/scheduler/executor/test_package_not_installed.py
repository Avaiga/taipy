import pytest

from taipy.task.scheduler.executor.remote_pool_executor import RemotePoolExecutor

try:
    from celery import Celery
except:
    ...
else:
    pytest.skip("skipping RemotePoolExecutor tests", allow_module_level=True)


def test_submit_one_argument():
    with pytest.raises(ImportError):
        RemotePoolExecutor(None, None)
