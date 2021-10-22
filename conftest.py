import os
import shutil

import pandas as pd
import pytest


@pytest.fixture(scope="function")
def csv_file(tmpdir_factory):
    csv = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.csv")
    csv.to_csv(str(fn), index=False)
    return fn


@pytest.fixture(scope="session")
def default_data_frame():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")
