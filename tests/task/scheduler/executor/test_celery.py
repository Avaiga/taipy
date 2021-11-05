from unittest.mock import MagicMock

import pytest

from taipy.task.scheduler.executor.remote_pool_executor import RemotePoolExecutor


def mult(nb1, nb2):
    return nb1 * nb2


def mult_by_two(nb):
    return mult(2, nb)


@pytest.fixture
def remote_pool_executor():
    class MockRemotePoolExecutor:
        def delay(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            return self

        def get(self):
            return RemotePoolExecutor._execute(*self.args, **self.kwargs)

    return MockRemotePoolExecutor()


@pytest.fixture
def celery(remote_pool_executor):
    r = RemotePoolExecutor(None)
    r.remote_executor = remote_pool_executor
    return r


def test_submit_one_argument(celery):
    res = celery.submit(mult_by_two, 21)
    assert res.result() == 42


def test_submit_two_arguments(celery):
    res = celery.submit(mult, 21, 4)
    assert res.result() == 84


def test_submit_two_arguments_in_context_manager(remote_pool_executor):
    with RemotePoolExecutor(None) as pool:
        pool.remote_executor = remote_pool_executor
        res = pool.submit(mult, 21, 4)
        assert res.result() == 84


def test_submit_raised(celery):
    res = celery.submit(mult_by_two, None)

    with pytest.raises(TypeError):
        res.result()
