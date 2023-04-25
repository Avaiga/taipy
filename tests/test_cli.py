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

import re
from unittest.mock import patch

import pytest

from src.taipy._cli import cli


def preprocess_stdout(stdout):
    stdout = stdout.replace("\n", " ").replace("\t", " ")
    return re.sub(" +", " ", stdout)


def test_taipy_help(capsys):
    with patch("sys.argv", ["prog", "--help"]):
        with pytest.raises(SystemExit):
            cli()
        expected_help = """[-h] {version,create} ...

positional arguments:
  {version,create}
    version         Taipy version control system.
    create          Create a new Taipy application.

options:
  -h, --help        show this help message and exit
"""
        out, _ = capsys.readouterr()

        assert preprocess_stdout(expected_help) in preprocess_stdout(out)


def test_taipy_version_help(capsys):
    with patch("sys.argv", ["prog", "version", "--help"]):
        with pytest.raises(SystemExit):
            cli()
        expected_help = """version [-h] [-l] [-d VERSION] [-dp VERSION]

options:
  -h, --help            show this help message and exit
  -l, --list            List all existing versions of the Taipy application.
  -d VERSION, --delete VERSION
                        Delete a Taipy version by version number.
  -dp VERSION, --delete-production VERSION
                        Delete a Taipy version from production by version number. The version is still kept as an
                        experiment version.
"""
        out, _ = capsys.readouterr()

        assert preprocess_stdout(expected_help) in preprocess_stdout(out)


def test_taipy_create_help(capsys):
    with patch("sys.argv", ["prog", "create", "--help"]):
        with pytest.raises(SystemExit):
            cli()
        expected_help = """create [-h] [--template {default}]

options:
  -h, --help            show this help message and exit
  --template {default}
                        The Taipy template to create new application.
"""
        out, _ = capsys.readouterr()

        assert preprocess_stdout(expected_help) in preprocess_stdout(out)
