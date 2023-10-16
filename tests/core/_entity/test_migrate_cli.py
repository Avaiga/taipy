# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import filecmp
import shutil
from unittest.mock import patch

import pytest

from src.taipy.core._entity._migrate_cli import _MigrateCLI


def test_migrate_fs_default(caplog):
    _MigrateCLI.create_parser()

    # Test migrate with default .data folder
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem"]):
            _MigrateCLI.parse_arguments()
    assert "Starting entity migration from .data folder" in caplog.text


def test_migrate_fs_specified_folder(caplog):
    _MigrateCLI.create_parser()

    # Copy data_sample to .data folder for testing
    data_sample_path = "tests/core/_entity/data_sample"
    data_path = "tests/core/_entity/.data"
    shutil.copytree(data_sample_path, data_path)

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path]):
            _MigrateCLI.parse_arguments()
    assert f"Starting entity migration from {data_path} folder" in caplog.text

    # Compare migrated .data folder with data_sample_migrated
    dircmp_result = filecmp.dircmp(data_path, "tests/core/_entity/data_sample_migrated")
    assert not dircmp_result.diff_files and not dircmp_result.left_only and not dircmp_result.right_only
    for subdir in dircmp_result.subdirs.values():
        assert not subdir.diff_files and not subdir.left_only and not subdir.right_only

    # Remove .data folder
    shutil.rmtree(data_path)


def test_migrate_fs_non_existing_folder(caplog):
    _MigrateCLI.create_parser()

    # Test migrate with a non-existing folder
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", "non-existing-folder"]):
            _MigrateCLI.parse_arguments()
    assert err.value.code == 1
    assert "Folder 'non-existing-folder' does not exist." in caplog.text

    caplog.clear()


@patch("src.taipy.core._entity._migrate_cli._migrate_sql_entities")
def test_migrate_sql_specified_path(_migrate_sql_entities_mock, tmp_sqlite):
    _MigrateCLI.create_parser()

    # Test the _migrate_sql_entities is called once with the correct path
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite]):
            _MigrateCLI.parse_arguments()
            assert _migrate_sql_entities_mock.assert_called_once_with(path=tmp_sqlite)


def test_migrate_sql_non_existing_path(caplog):
    _MigrateCLI.create_parser()

    # Test migrate without providing a path
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql"]):
            _MigrateCLI.parse_arguments()

    assert err.value.code == 1
    assert "Missing the required sqlite path." in caplog.text

    caplog.clear()

    # Test migrate with a non-existing-path.sqlite file
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", "non-existing-path.sqlite"]):
            _MigrateCLI.parse_arguments()
    assert err.value.code == 1
    assert "File 'non-existing-path.sqlite' does not exist." in caplog.text


@patch("src.taipy.core._entity._migrate_cli._migrate_mongo_entities")
def test_call_to_migrate_mongo(_migrate_mongo_entities_mock):
    _MigrateCLI.create_parser()

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo"]):
            _MigrateCLI.parse_arguments()
            assert _migrate_mongo_entities_mock.assert_called_once_with()

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo", "host", "port", "user", "password"]):
            _MigrateCLI.parse_arguments()
            assert _migrate_mongo_entities_mock.assert_called_once_with("host", "port", "user", "password")
