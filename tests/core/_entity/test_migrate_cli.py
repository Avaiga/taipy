# Copyright 2021-2024 Avaiga Private Limited
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
import os
import shutil
import sys
from sqlite3 import OperationalError
from unittest.mock import patch

import mongomock
import pytest

from taipy._entrypoint import _entrypoint
from taipy.core._entity._migrate_cli import _MigrateCLI


def test_migrate_cli_with_wrong_repository_type_arguments(caplog):
    with patch("sys.argv", ["prog", "migrate", "--reposiory-tyep", "filesystem"]):
        with pytest.raises(SystemExit):
            _entrypoint()
        assert "Unknown arguments: --reposiory-tyep. Did you mean: --repository-type?" in caplog.text


def test_migrate_cli_with_wrong_skip_backup_arguments(caplog):
    with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", "--slip-backup"]):
        with pytest.raises(SystemExit):
            _entrypoint()
        assert "Unknown arguments: --slip-backup. Did you mean: --skip-backup?" in caplog.text


@pytest.fixture(scope="function", autouse=True)
def clean_data_folder():
    if os.path.exists("tests/core/_entity/.data"):
        shutil.rmtree("tests/core/_entity/.data")
    if os.path.exists("tests/core/_entity/.taipy"):
        shutil.rmtree("tests/core/_entity/.taipy")
    yield


def test_migrate_fs_default(caplog):
    _MigrateCLI.create_parser()

    # Test migrate with default .data folder
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", "--skip-backup"]):
            _MigrateCLI.handle_command()
    assert "Starting entity migration from '.taipy/' folder" in caplog.text


def test_migrate_fs_specified_folder(caplog, mocker):
    mocker.patch("taipy.core._entity._migrate._utils.version", return_value="3.1.0")
    _MigrateCLI.create_parser()

    # Copy data_sample to .data folder for testing
    data_sample_path = "tests/core/_entity/data_sample"
    data_path = "tests/core/_entity/.data"
    shutil.copytree(data_sample_path, data_path)

    # Run with --skip-backup to only test the migration
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path, "--skip-backup"]):
            _MigrateCLI.handle_command()
    assert f"Starting entity migration from '{data_path}' folder" in caplog.text

    # Compare migrated .data folder with data_sample_migrated
    dircmp_result = filecmp.dircmp(data_path, "tests/core/_entity/data_sample_migrated")

    assert not dircmp_result.diff_files and not dircmp_result.left_only and not dircmp_result.right_only
    for subdir in dircmp_result.subdirs.values():
        assert not subdir.diff_files and not subdir.left_only and not subdir.right_only


def test_migrate_fs_backup_and_remove(caplog, mocker):
    mocker.patch("taipy.core._entity._migrate._utils.version", return_value="3.1.0")
    _MigrateCLI.create_parser()

    # Copy data_sample to .data folder for testing
    data_sample_path = "tests/core/_entity/data_sample"
    data_path = "tests/core/_entity/.data"
    backup_path = "tests/core/_entity/.data_backup"
    shutil.copytree(data_sample_path, data_path)

    # Remove backup when it does not exist should raise an error
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path, "--remove-backup"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert f"The backup folder '{backup_path}' does not exist." in caplog.text
    assert not os.path.exists(backup_path)

    # Run without --skip-backup to create the backup folder
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path]):
            _MigrateCLI.handle_command()
    assert f"Backed up entities from '{data_path}' to '{backup_path}' folder before migration." in caplog.text

    assert os.path.exists(backup_path)

    # Remove backup
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path, "--remove-backup"]):
            _MigrateCLI.handle_command()
    assert f"Removed backup entities from the backup folder '{backup_path}'." in caplog.text
    assert not os.path.exists(backup_path)


def test_migrate_fs_backup_and_restore(caplog, mocker):
    mocker.patch("taipy.core._entity._migrate._utils.version", return_value="3.1.0")
    _MigrateCLI.create_parser()

    # Copy data_sample to .data folder for testing
    data_sample_path = "tests/core/_entity/data_sample"
    data_path = "tests/core/_entity/.data"
    backup_path = "tests/core/_entity/.data_backup"
    shutil.copytree(data_sample_path, data_path)

    # Restore backup when it does not exist should raise an error
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path, "--restore"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert f"The backup folder '{backup_path}' does not exist." in caplog.text
    assert not os.path.exists(backup_path)

    # Run without --skip-backup to create the backup folder
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path]):
            _MigrateCLI.handle_command()

    assert os.path.exists(backup_path)

    # restore the backup
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", data_path, "--restore"]):
            _MigrateCLI.handle_command()
    assert f"Restored entities from the backup folder '{backup_path}' to '{data_path}'." in caplog.text
    assert not os.path.exists(backup_path)

    # Compare migrated .data folder with data_sample to ensure restoring the backup worked
    dircmp_result = filecmp.dircmp(data_path, "tests/core/_entity/data_sample")
    assert not dircmp_result.diff_files and not dircmp_result.left_only and not dircmp_result.right_only
    for subdir in dircmp_result.subdirs.values():
        assert not subdir.diff_files and not subdir.left_only and not subdir.right_only


def test_migrate_fs_non_existing_folder(caplog):
    _MigrateCLI.create_parser()

    # Test migrate with a non-existing folder
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "filesystem", "non-existing-folder"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert "Folder 'non-existing-folder' does not exist." in caplog.text


@patch("taipy.core._entity._migrate_cli._migrate_sql_entities")
def test_migrate_sql_specified_path(_migrate_sql_entities_mock, tmp_sqlite):
    _MigrateCLI.create_parser()

    # Test the _migrate_sql_entities is called once with the correct path
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite, "--skip-backup"]):
            _MigrateCLI.handle_command()
            assert _migrate_sql_entities_mock.assert_called_once_with(path=tmp_sqlite)


def test_migrate_sql_backup_and_remove(caplog, tmp_sqlite):
    _MigrateCLI.create_parser()

    # Create the .sqlite file to test
    with open(tmp_sqlite, "w") as f:
        f.write("")

    file_name, file_extension = tmp_sqlite.rsplit(".", 1)
    backup_sqlite = f"{file_name}_backup.{file_extension}"

    # Remove backup when it does not exist should raise an error
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite, "--remove-backup"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert f"The backup database '{backup_sqlite}' does not exist." in caplog.text
    assert not os.path.exists(backup_sqlite)

    # Run without --skip-backup to create the backup database
    with pytest.raises((SystemExit, OperationalError)):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite]):
            _MigrateCLI.handle_command()

    assert os.path.exists(backup_sqlite)

    # Remove backup
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite, "--remove-backup"]):
            _MigrateCLI.handle_command()
    assert f"Removed backup entities from the backup database '{backup_sqlite}'." in caplog.text
    assert not os.path.exists(backup_sqlite)


def test_migrate_sql_backup_and_restore(caplog, tmp_sqlite):
    _MigrateCLI.create_parser()

    # Create the .sqlite file to test
    with open(tmp_sqlite, "w") as f:
        f.write("")

    file_name, file_extension = tmp_sqlite.rsplit(".", 1)
    backup_sqlite = f"{file_name}_backup.{file_extension}"

    # Restore backup when it does not exist should raise an error
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite, "--restore"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert f"The backup database '{backup_sqlite}' does not exist." in caplog.text
    assert not os.path.exists(backup_sqlite)

    # Run without --skip-backup to create the backup database
    with pytest.raises((SystemExit, OperationalError)):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite]):
            _MigrateCLI.handle_command()

    assert os.path.exists(backup_sqlite)

    # Restore the backup
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", tmp_sqlite, "--restore"]):
            _MigrateCLI.handle_command()
    assert f"Restored entities from the backup database '{backup_sqlite}' to '{tmp_sqlite}'." in caplog.text
    assert not os.path.exists(backup_sqlite)


def test_migrate_sql_non_existing_path(caplog):
    _MigrateCLI.create_parser()

    # Test migrate without providing a path
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql"]):
            _MigrateCLI.handle_command()

    assert err.value.code == 1
    assert "Missing the required sqlite path." in caplog.text

    caplog.clear()

    # Test migrate with a non-existing-path.sqlite file
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "sql", "non-existing-path.sqlite"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert "File 'non-existing-path.sqlite' does not exist." in caplog.text


@patch("taipy.core._entity._migrate_cli._migrate_mongo_entities")
def test_call_to_migrate_mongo(_migrate_mongo_entities_mock):
    _MigrateCLI.create_parser()

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo"]):
            _MigrateCLI.handle_command()
            assert _migrate_mongo_entities_mock.assert_called_once_with()

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo", "host", "port", "user", "password"]):
            _MigrateCLI.handle_command()
            assert _migrate_mongo_entities_mock.assert_called_once_with("host", "port", "user", "password")


@mongomock.patch(servers=(("localhost", 27017),))
def test_migrate_mongo_backup_and_remove(caplog):
    _MigrateCLI.create_parser()

    mongo_backup_path = ".mongo_backup"

    # Remove backup when it does not exist should raise an error
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo", "--remove-backup"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert f"The backup folder '{mongo_backup_path}' does not exist." in caplog.text
    assert not os.path.exists(mongo_backup_path)

    # Run without --skip-backup to create the backup database
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo"]):
            _MigrateCLI.handle_command()

    assert os.path.exists(mongo_backup_path)

    # Remove backup
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo", "--remove-backup"]):
            _MigrateCLI.handle_command()
    assert f"Removed backup entities from the backup folder '{mongo_backup_path}'." in caplog.text
    assert not os.path.exists(mongo_backup_path)


@mongomock.patch(servers=(("localhost", 27017),))
def test_migrate_mongo_backup_and_restore(caplog):
    _MigrateCLI.create_parser()

    mongo_backup_path = ".mongo_backup"

    # Restore backup when it does not exist should raise an error
    with pytest.raises(SystemExit) as err:
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo", "--restore"]):
            _MigrateCLI.handle_command()
    assert err.value.code == 1
    assert f"The backup folder '{mongo_backup_path}' does not exist." in caplog.text
    assert not os.path.exists(mongo_backup_path)

    # Run without --skip-backup to create the backup database
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo"]):
            _MigrateCLI.handle_command()

    assert os.path.exists(mongo_backup_path)

    # Restore the backup
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "mongo", "--restore"]):
            _MigrateCLI.handle_command()
    assert f"Restored entities from the backup folder '{mongo_backup_path}'." in caplog.text
    assert not os.path.exists(mongo_backup_path)


def test_not_provide_valid_repository_type(caplog):
    _MigrateCLI.create_parser()

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate"]):
            _MigrateCLI.handle_command()
            assert "the following arguments are required: --repository-type" in caplog.text

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type"]):
            _MigrateCLI.handle_command()
            assert "argument --repository-type: expected at least one argument" in caplog.text

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "migrate", "--repository-type", "invalid-repository-type"]):
            _MigrateCLI.handle_command()
            assert "Unknown repository type invalid-repository-type" in caplog.text
