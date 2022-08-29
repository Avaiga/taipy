import os
from unittest import mock

from src.taipy.config import Config
from src.taipy.config.common.scope import Scope
from src.taipy.config.common.frequency import Frequency
from tests.config.utils.named_temporary_file import NamedTemporaryFile
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def test_write_configuration_file():
    expected_config = """
[TAIPY]
root_folder = "./taipy/"
storage_folder = ".data/"
clean_entities_enabled = "True:bool"

[unique_section_name]
attribute = "my_attribute"
prop = "my_prop"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "p1",]
prop_scope = "SCENARIO:SCOPE"
prop_freq = "QUARTERLY:FREQUENCY"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[section_name.default]
attribute = "default_attribute"
prop = "default_prop"
prop_int = "0:int"

[section_name.my_id]
attribute = "my_attribute"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "unique_section_name:SECTION",]
prop_scope = "SCENARIO"
baz = "ENV[QUX]"
    """.strip()
    tf = NamedTemporaryFile()
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.configure_global_app(clean_entities_enabled=True)
        unique_section = Config.configure_unique_section_for_tests(
            attribute="my_attribute",
            prop="my_prop",
            prop_int=1,
            prop_bool=False,
            prop_list=["p1", ],
            prop_scope=Scope.SCENARIO,
            prop_freq=Frequency.QUARTERLY,
            baz="ENV[QUX]",
            quux="ENV[QUUZ]:bool",
            corge=("grault", "ENV[GARPLY]", "ENV[WALDO]:int", 3.0))
        Config.configure_section_for_tests("my_id", "my_attribute",
                                           prop_int=1,
                                           prop_bool=False,
                                           prop_list=[unique_section],
                                           prop_scope="SCENARIO",
                                           baz="ENV[QUX]")
        Config.export(tf.filename)
        actual_config = tf.read().strip()
        assert actual_config == expected_config

        # Config._default_config = _Config()._default_config()
        # Config._python_config = _Config()
        # Config._file_config = None
        # Config._env_file_config = None
        # Config._applied_config = _Config._default_config()
        # Config._register_default(UniqueSectionForTest("default_attribute"))
        # Config.configure_unique_section_for_tests = UniqueSectionForTest._configure
        # Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute",
        #                                         prop="default_prop",
        #                                         prop_int="0:int"))
        # Config.configure_section_for_tests = SectionForTest._configure
        #
        # Config.load(tf.filename)
        # tf2 = NamedTemporaryFile()
        # Config.export(tf2.filename)
        #
        # actual_config_2 = tf2.read().strip()
        # assert actual_config_2 == expected_config


def test_read_configuration_file():
    config = """
[TAIPY]
root_folder = "./taipy/"
storage_folder = ".data/"
clean_entities_enabled = "True:bool"

[unique_section_name]
attribute = "my_attribute"
prop = "my_prop"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "p1",]
prop_scope = "SCENARIO:SCOPE"
prop_freq = "QUARTERLY:FREQUENCY"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[section_name.default]
attribute = "default_attribute"
prop = "default_prop"
prop_int = "0:int"

[section_name.my_id]
attribute = "my_attribute"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "unique_section_name", "section_name.my_id",]
prop_scope = "SCENARIO:SCOPE"
baz = "ENV[QUX]"
    """.strip()
    tf = NamedTemporaryFile(config)
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.load(tf.filename)

        assert Config.unique_sections is not None
        assert Config.unique_sections[UniqueSectionForTest.name] is not None
        assert Config.unique_sections[UniqueSectionForTest.name].attribute == "my_attribute"
        assert Config.unique_sections[UniqueSectionForTest.name].prop == "my_prop"
        assert Config.unique_sections[UniqueSectionForTest.name].prop_int == 1
        assert Config.unique_sections[UniqueSectionForTest.name].prop_bool is False
        assert Config.unique_sections[UniqueSectionForTest.name].prop_list == ["p1", ]
        assert Config.unique_sections[UniqueSectionForTest.name].prop_scope == Scope.SCENARIO
        assert Config.unique_sections[UniqueSectionForTest.name].prop_freq == Frequency.QUARTERLY
        assert Config.unique_sections[UniqueSectionForTest.name].baz == "qux"
        assert Config.unique_sections[UniqueSectionForTest.name].quux == True
        assert Config.unique_sections[UniqueSectionForTest.name].corge == ["grault", "garply", 17, 3.0, ]

        assert Config.sections is not None
        assert len(Config.sections) == 1
        assert Config.sections[SectionForTest.name] is not None
        assert len(Config.sections[SectionForTest.name]) == 2
        assert Config.sections[SectionForTest.name]["default"] is not None
        assert Config.sections[SectionForTest.name]["default"].attribute == "default_attribute"
        assert Config.sections[SectionForTest.name]["default"].prop == "default_prop"
        assert Config.sections[SectionForTest.name]["default"].prop_int == 0
        assert Config.sections[SectionForTest.name]["my_id"] is not None
        assert Config.sections[SectionForTest.name]["my_id"].attribute == "my_attribute"
        assert Config.sections[SectionForTest.name]["my_id"].prop is None
        assert Config.sections[SectionForTest.name]["my_id"].prop_int == 1
        assert Config.sections[SectionForTest.name]["my_id"].prop_bool is False
        assert Config.sections[SectionForTest.name]["my_id"].prop_list == ["unique_section_name", "section_name.my_id"]
        assert Config.sections[SectionForTest.name]["my_id"].prop_scope == Scope.SCENARIO
        assert Config.sections[SectionForTest.name]["my_id"].baz == "qux"

        tf2 = NamedTemporaryFile()
        Config.export(tf2.filename)
        actual_config_2 = tf2.read().strip()
        assert actual_config_2 == config
