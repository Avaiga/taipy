import os
import shutil

import pytest


@pytest.fixture(autouse=True)
def cleanup_files():
    path = os.path.join(os.path.abspath(os.getcwd()), ".data")
    if os.path.exists(path):
        shutil.rmtree(path)
