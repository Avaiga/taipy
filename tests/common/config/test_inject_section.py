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

from taipy.common.config import Config, _inject_section
from taipy.common.config._serializer._base_serializer import _BaseSerializer
from tests.common.config.utils.section_for_tests import SectionForTest
from tests.common.config.utils.serializable_object_for_test import SerializableObjectForTest


@pytest.fixture(scope="function", autouse=True)
def reset(reset_configuration_singleton):
    reset_configuration_singleton()

    yield


def test_inject_section():
    assert not hasattr(Config, "sectionfortest")
    assert SerializableObjectForTest._type_identifier() not in _BaseSerializer._SERIALIZABLE_TYPES

    _inject_section(
        SectionForTest,
        "sectionfortest",
        SectionForTest("default"),
        [("configure_scenario", SectionForTest._configure)],
    )

    assert hasattr(Config, "sectionfortest")
    assert SerializableObjectForTest._type_identifier() in _BaseSerializer._SERIALIZABLE_TYPES
