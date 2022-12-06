# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pytest

from src.taipy.core._version._version import _Version
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.exceptions.exceptions import VersionAlreadyExists
from taipy.config.config import Config


def test_save_and_get_version_entity(tmpdir):
    _VersionManager._repository.base_path = tmpdir
    assert len(_VersionManager._get_all()) == 0

    version = _Version(id="foo", config=Config._applied_config)

    _VersionManager.get_or_create(id="foo", override=False)

    version_1 = _VersionManager._get(version.id)
    assert version_1.id == version.id
    assert Config._serializer._str(version_1.config) == Config._serializer._str(version.config)

    assert len(_VersionManager._get_all()) == 1
    assert _VersionManager._get(version.id) == version


def test_save_existing_version_should_fail(tmpdir):
    _VersionManager._repository.base_path = tmpdir

    _VersionManager.get_or_create(id="foo", override=False)

    with pytest.raises(VersionAlreadyExists):
        _VersionManager.get_or_create(id="foo", override=False)
