import os
from unittest import mock

import pytest

from src.taipy.config.exceptions.exceptions import InvalidConfigurationId
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


class WrongUniqueSection(UniqueSectionForTest):
    name = "1wrong_id"


class WrongSection(SectionForTest):
    name = "correct_name"


def test_section_uses_valid_id():
    with pytest.raises(InvalidConfigurationId):
        WrongUniqueSection(attribute="foo")
    with pytest.raises(InvalidConfigurationId):
        WrongSection("wrong id", attribute="foo")
    with pytest.raises(InvalidConfigurationId):
        WrongSection("1wrong_id", attribute="foo")
    with pytest.raises(InvalidConfigurationId):
        WrongSection("wrong_@id", attribute="foo")


def test_templated_properties_are_replaced():
    with mock.patch.dict(os.environ, {"foo": "bar", "baz": "1"}):
        u_sect = UniqueSectionForTest(attribute="attribute", tpl_property="ENV[foo]")
        assert u_sect.tpl_property == "bar"

        sect = SectionForTest(id="my_id", attribute="attribute", tpl_property="ENV[baz]:int")
        assert sect.tpl_property == 1
