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

import pytest

from src.taipy.config.config import Config
from src.taipy.config.exceptions.exceptions import LoadingError
from tests.config.utils.named_temporary_file import NamedTemporaryFile


def test_node_can_not_appear_twice():
    config = NamedTemporaryFile(
        """
[unique_section_name]
attribute = "my_attribute"

[unique_section_name]
attribute = "other_attribute"
    """
    )

    with pytest.raises(LoadingError, match="Can not load configuration"):
        Config.load(config.filename)


def test_skip_configuration_outside_nodes():
    config = NamedTemporaryFile(
        """
foo = "bar"
    """
    )

    Config.load(config.filename)
    assert Config.global_config.foo is None
