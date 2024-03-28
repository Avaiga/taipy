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

from unittest.mock import patch

import pytest

from taipy._entrypoint import _entrypoint


def test_create_cli_with_wrong_arguments(caplog):
    with patch("sys.argv", ["prog", "create", "--teamplaet", "default"]):
        with pytest.raises(SystemExit):
            _entrypoint()
        assert "Unknown arguments: --teamplaet. Did you mean: --template?" in caplog.text


def test_create_cli_with_unsupported_template(capsys):
    with patch("sys.argv", ["prog", "create", "--template", "not-a-template"]):
        with pytest.raises(SystemExit):
            _entrypoint()
        _, err = capsys.readouterr()
        assert "invalid choice: 'not-a-template'" in err
