# Copyright 2021-2025 Avaiga Private Limited
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

from tools.release.common import Version


def test_from_string():
    with pytest.raises(ValueError):
        Version.from_string("invalid")
    with pytest.raises(ValueError):
        Version.from_string("1")
    with pytest.raises(ValueError):
        Version.from_string("1.x.2")

    version = Version.from_string("1.2")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 0
    assert version.ext is None

    version = Version.from_string("1.2.3")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.ext is None

    version = Version.from_string("1.2.3.some_ext")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.ext == "some_ext"

    version = Version.from_string("1.2.3.some_ext.more_ext")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.ext == "some_ext.more_ext"


def test_split_extension():
    version = Version.from_string("1.2.3")
    extension = version.split_ext()
    assert extension == ("", -1)

    version = Version.from_string("1.2.3.some_ext")
    extension = version.split_ext()
    assert extension == ("some_ext", -1)

    version = Version.from_string("1.2.3.some_ext123")
    extension = version.split_ext()
    assert extension == ("some_ext", 123)


def test_to_string():
    version = Version(major=1, minor=2)
    assert str(version) == "1.2.0"

    version = Version(major=1, minor=2, patch=3)
    assert str(version) == "1.2.3"

    version = Version(major=1, minor=2, patch=3, ext="some_ext")
    assert str(version) == "1.2.3.some_ext"


def test_to_dict():
    version = Version(major=1, minor=2, patch=3)
    assert version.to_dict() == {"major": 1, "minor": 2, "patch": 3}

    version = Version(major=1, minor=2, patch=3, ext="some_ext")
    assert version.to_dict() == {"major": 1, "minor": 2, "patch": 3, "ext": "some_ext"}


def test_compatibility():
    # Different major version number
    v1 = Version(major=1, minor=2, patch=3)
    v2 = Version(major=2, minor=2, patch=3)
    assert not v1.is_compatible(v2), "Major versions differ"

    # Different minor version number
    v1 = Version(major=1, minor=2, patch=3)
    v2 = Version(major=1, minor=3, patch=3)
    assert not v1.is_compatible(v2), "Minor versions differ"

    # All the same
    v1 = Version(major=1, minor=2, patch=3)
    v2 = Version(major=1, minor=2, patch=3)
    assert v1.is_compatible(v2), "Identical versions"

    # Greater patch number
    v1 = Version(major=1, minor=2, patch=4)
    v2 = Version(major=1, minor=2, patch=3)
    assert v1.is_compatible(v2), "Patch number is greater"

    # Smaller patch number
    v1 = Version(major=1, minor=2, patch=3)
    v2 = Version(major=1, minor=2, patch=4)
    assert v1.is_compatible(v2), "Patch number is smaller"

    # Same patch number, extension
    v1 = Version(major=1, minor=2, patch=3, ext="ext")
    v2 = Version(major=1, minor=2, patch=3)
    assert v1.is_compatible(v2), "Same version, with extension"

    # Same patch number, no extension
    v1 = Version(major=1, minor=2, patch=3)
    v2 = Version(major=1, minor=2, patch=3, ext="ext")
    assert not v1.is_compatible(v2), "Same version, no extension is expected"

    # Same patch number, different extension
    v1 = Version(major=1, minor=2, patch=3, ext="some_ext")
    v2 = Version(major=1, minor=2, patch=3, ext="another_ext")
    assert not v1.is_compatible(v2), "Same version, different extensions"


def test_order():
    v1 = Version(major=1, minor=0)
    v2 = Version(major=2, minor=0)
    assert v1 < v2, "Version 1.0 is older than 2.0"
    assert v2 > v1, "Version 2.0 is newer than 1.0"

    v1 = Version(major=1, minor=0)
    v2 = Version(major=1, minor=1)
    assert v1 < v2, "Version 1.0 is older than 1.1"
    assert v2 > v1, "Version 1.1 is newer than 1.0"

    v1 = Version(major=1, minor=2)
    v2 = Version(major=2, minor=1)
    assert v1 < v2, "Version 1.2 is older than 2.1"
    assert v2 > v1, "Version 2.1 is newer than 1.2"

    v1 = Version(major=1, minor=0)
    v2 = Version(major=1, minor=0, patch=1)
    assert v1 < v2, "Version 1.0.0 is older than 1.0.1"
    assert v2 > v1, "Version 1.0.1 is newer than 1.0.0"

    v1 = Version(major=1, minor=2, patch=3)
    v2 = Version(major=1, minor=2, patch=3, ext="dev0")
    assert v1 > v2, "Version 1.2.3 is newer than 1.2.3.dev0"
    assert v2 < v1, "Version 1.2.3.dev0 is older than 1.2.3"

    v1 = Version(major=1, minor=2, patch=3, ext="dev0")
    v2 = Version(major=1, minor=2, patch=3, ext="dev1")
    assert v1 < v2, "Version 1.2.3.dev0 is older than 1.2.3.dev1"
    assert v2 > v1, "Version 1.2.3.dev1 is newer 1.2.3.dev0"

    versions = [Version(1, 0), Version(2, 1), Version(3, 4), Version(2, 0)]
    assert max(versions) == Version(3, 4), "Cannot find max in Version list"


def test_has_extension():
    version = Version.from_string("1.2.3")
    assert not version.has_extension()

    version = Version.from_string("1.2.3.dev")
    assert version.has_extension()

    version = Version.from_string("1.2.3.dev0")
    assert version.has_extension()


def test_validate_extension():
    version = Version.from_string("1.2.3")
    assert not version.validate_extension("dev")

    version = Version.from_string("1.2.3.dev")
    assert version.validate_extension("dev")
    assert not version.validate_extension("rc")

    version = Version.from_string("1.2.3.dev0")
    assert version.validate_extension("dev")

    version = Version.from_string("1.2.3.rc1")
    assert version.validate_extension("rc")
    assert not version.validate_extension("dev")
