import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": "http://localhost:5000",
        "timezone_id": "Europe/Paris",
    }
