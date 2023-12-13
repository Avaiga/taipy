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

import datetime
import json
import os
from unittest import mock

from taipy.config import Config
from taipy.config._serializer._json_serializer import _JsonSerializer
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from tests.config.utils.named_temporary_file import NamedTemporaryFile
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def add(a, b):
    return a + b


class CustomClass:
    a = None
    b = None


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        return (
            {"__type__": "Datetime", "__value__": o.isoformat()}
            if isinstance(o, datetime)
            else json.JSONEncoder.default(self, o)
        )


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source):
        if source.get("__type__") == "Datetime":
            return datetime.fromisoformat(source.get("__value__"))
        else:
            return source


def test_write_toml_configuration_file():
    expected_toml_config = """
[TAIPY]

[unique_section_name]
attribute = "my_attribute"
prop = "my_prop"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "p1", "1991-01-01T00:00:00:datetime", "1d0h0m0s:timedelta",]
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
prop = "default_prop"
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
        unique_section = Config.configure_unique_section_for_tests(
            attribute="my_attribute",
            prop="my_prop",
            prop_int=1,
            prop_bool=False,
            prop_list=["p1", datetime.datetime(1991, 1, 1), datetime.timedelta(days=1)],
            prop_scope=Scope.SCENARIO,
            prop_freq=Frequency.QUARTERLY,
            baz="ENV[QUX]",
            quux="ENV[QUUZ]:bool",
            corge=("grault", "ENV[GARPLY]", "ENV[WALDO]:int", 3.0),
        )
        Config.configure_section_for_tests(
            "my_id",
            "my_attribute",
            prop_int=1,
            prop_bool=False,
            prop_list=[unique_section],
            prop_scope="SCENARIO",
            baz="ENV[QUX]",
        )

        Config.backup(tf.filename)
        actual_config = tf.read().strip()
        assert actual_config == expected_toml_config


def test_read_toml_configuration_file():
    toml_config = """
[TAIPY]
foo = "bar"

[unique_section_name]
attribute = "my_attribute"
prop = "my_prop"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "p1", "1991-01-01T00:00:00:datetime", "1d0h0m0s:timedelta",]
prop_scope = "SCENARIO:SCOPE"
prop_freq = "QUARTERLY:FREQUENCY"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[TAIPY.custom_properties]
bar = "baz"

[section_name.default]
attribute = "default_attribute"
prop = "default_prop"
prop_int = "0:int"

[section_name.my_id]
attribute = "my_attribute"
prop = "default_prop"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "unique_section_name", "section_name.my_id",]
prop_scope = "SCENARIO:SCOPE"
baz = "ENV[QUX]"
    """.strip()
    tf = NamedTemporaryFile(toml_config)
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.override(tf.filename)

        assert Config.global_config.foo == "bar"
        assert Config.global_config.custom_properties.get("bar") == "baz"

        assert Config.unique_sections is not None
        assert Config.unique_sections[UniqueSectionForTest.name] is not None
        assert Config.unique_sections[UniqueSectionForTest.name].attribute == "my_attribute"
        assert Config.unique_sections[UniqueSectionForTest.name].prop == "my_prop"
        assert Config.unique_sections[UniqueSectionForTest.name].prop_int == 1
        assert Config.unique_sections[UniqueSectionForTest.name].prop_bool is False
        assert Config.unique_sections[UniqueSectionForTest.name].prop_list == [
            "p1",
            datetime.datetime(1991, 1, 1),
            datetime.timedelta(days=1),
        ]
        assert Config.unique_sections[UniqueSectionForTest.name].prop_scope == Scope.SCENARIO
        assert Config.unique_sections[UniqueSectionForTest.name].prop_freq == Frequency.QUARTERLY
        assert Config.unique_sections[UniqueSectionForTest.name].baz == "qux"
        assert Config.unique_sections[UniqueSectionForTest.name].quux is True
        assert Config.unique_sections[UniqueSectionForTest.name].corge == [
            "grault",
            "garply",
            17,
            3.0,
        ]

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
        assert Config.sections[SectionForTest.name]["my_id"].prop == "default_prop"
        assert Config.sections[SectionForTest.name]["my_id"].prop_int == 1
        assert Config.sections[SectionForTest.name]["my_id"].prop_bool is False
        assert Config.sections[SectionForTest.name]["my_id"].prop_list == ["unique_section_name", "section_name.my_id"]
        assert Config.sections[SectionForTest.name]["my_id"].prop_scope == Scope.SCENARIO
        assert Config.sections[SectionForTest.name]["my_id"].baz == "qux"

        tf2 = NamedTemporaryFile()
        Config.backup(tf2.filename)
        actual_config_2 = tf2.read().strip()
        assert actual_config_2 == toml_config


def test_read_write_toml_configuration_file_with_function_and_class():
    expected_toml_config = """
[TAIPY]

[unique_section_name]
attribute = "my_attribute"
prop = "my_prop"
prop_list = [ "tests.config.test_section_serialization.CustomEncoder:class", \
"tests.config.test_section_serialization.CustomDecoder:class",]

[section_name.default]
attribute = "default_attribute"
prop = "default_prop"
prop_int = "0:int"

[section_name.my_id]
attribute = "my_attribute"
prop = "default_prop"
prop_int = "0:int"
prop_fct_list = [ "tests.config.test_section_serialization.add:function",]
prop_class_list = [ "tests.config.test_section_serialization.CustomClass:class",]

[section_name.my_id_2]
attribute = "my_attribute_2"
prop = "default_prop"
prop_int = "0:int"
prop_fct_list = [ "builtins.print:function", "builtins.pow:function",]
    """.strip()

    tf = NamedTemporaryFile()
    Config.configure_unique_section_for_tests(
        attribute="my_attribute",
        prop="my_prop",
        prop_list=[CustomEncoder, CustomDecoder],
    )
    Config.configure_section_for_tests(
        "my_id",
        "my_attribute",
        prop_fct_list=[add],
        prop_class_list=[CustomClass],
    )

    Config.configure_section_for_tests(
        "my_id_2",
        "my_attribute_2",
        prop_fct_list=[print, pow],
    )

    Config.backup(tf.filename)
    actual_exported_toml = tf.read().strip()
    assert actual_exported_toml == expected_toml_config

    Config.override(tf.filename)
    tf2 = NamedTemporaryFile()
    Config.backup(tf2.filename)

    actual_exported_toml_2 = tf2.read().strip()
    assert actual_exported_toml_2 == expected_toml_config


def test_write_json_configuration_file():
    expected_json_config = """
{
"TAIPY": {},
"unique_section_name": {
"attribute": "my_attribute",
"prop": "my_prop",
"prop_int": "1:int",
"prop_bool": "False:bool",
"prop_list": [
"p1",
"1991-01-01T00:00:00:datetime",
"1d0h0m0s:timedelta"
],
"prop_scope": "SCENARIO:SCOPE",
"prop_freq": "QUARTERLY:FREQUENCY"
},
"section_name": {
"default": {
"attribute": "default_attribute",
"prop": "default_prop",
"prop_int": "0:int"
},
"my_id": {
"attribute": "my_attribute",
"prop": "default_prop",
"prop_int": "1:int",
"prop_bool": "False:bool",
"prop_list": [
"unique_section_name:SECTION"
],
"prop_scope": "SCENARIO",
"baz": "ENV[QUX]"
}
}
}
    """.strip()
    tf = NamedTemporaryFile()
    Config._serializer = _JsonSerializer()

    unique_section = Config.configure_unique_section_for_tests(
        attribute="my_attribute",
        prop="my_prop",
        prop_int=1,
        prop_bool=False,
        prop_list=["p1", datetime.datetime(1991, 1, 1), datetime.timedelta(days=1)],
        prop_scope=Scope.SCENARIO,
        prop_freq=Frequency.QUARTERLY,
    )
    Config.configure_section_for_tests(
        "my_id",
        "my_attribute",
        prop_int=1,
        prop_bool=False,
        prop_list=[unique_section],
        prop_scope="SCENARIO",
        baz="ENV[QUX]",
    )
    Config.backup(tf.filename)
    actual_config = tf.read()
    assert actual_config == expected_json_config


def test_read_json_configuration_file():
    json_config = """
{
"TAIPY": {
"root_folder": "./taipy/",
"storage_folder": ".data/",
"repository_type": "filesystem"
},
"unique_section_name": {
"attribute": "my_attribute",
"prop": "my_prop",
"prop_int": "1:int",
"prop_bool": "False:bool",
"prop_list": [
"p1",
"1991-01-01T00:00:00:datetime",
"1d0h0m0s:timedelta"
],
"prop_scope": "SCENARIO:SCOPE",
"prop_freq": "QUARTERLY:FREQUENCY"
},
"section_name": {
"default": {
"attribute": "default_attribute",
"prop": "default_prop",
"prop_int": "0:int"
},
"my_id": {
"attribute": "my_attribute",
"prop": "default_prop",
"prop_int": "1:int",
"prop_bool": "False:bool",
"prop_list": [
"unique_section_name"
],
"prop_scope": "SCENARIO"
}
}
}
    """.strip()
    Config._serializer = _JsonSerializer()
    tf = NamedTemporaryFile(json_config)

    Config.override(tf.filename)

    assert Config.unique_sections is not None
    assert Config.unique_sections[UniqueSectionForTest.name] is not None
    assert Config.unique_sections[UniqueSectionForTest.name].attribute == "my_attribute"
    assert Config.unique_sections[UniqueSectionForTest.name].prop == "my_prop"
    assert Config.unique_sections[UniqueSectionForTest.name].prop_int == 1
    assert Config.unique_sections[UniqueSectionForTest.name].prop_bool is False
    assert Config.unique_sections[UniqueSectionForTest.name].prop_list == [
        "p1",
        datetime.datetime(1991, 1, 1),
        datetime.timedelta(days=1),
    ]
    assert Config.unique_sections[UniqueSectionForTest.name].prop_scope == Scope.SCENARIO
    assert Config.unique_sections[UniqueSectionForTest.name].prop_freq == Frequency.QUARTERLY

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
    assert Config.sections[SectionForTest.name]["my_id"].prop == "default_prop"
    assert Config.sections[SectionForTest.name]["my_id"].prop_int == 1
    assert Config.sections[SectionForTest.name]["my_id"].prop_bool is False
    assert Config.sections[SectionForTest.name]["my_id"].prop_list == ["unique_section_name"]

    tf2 = NamedTemporaryFile()
    Config.backup(tf2.filename)
    actual_config_2 = tf2.read().strip()
    assert actual_config_2 == json_config


def test_read_write_json_configuration_file_with_function_and_class():
    expected_json_config = """
{
"TAIPY": {},
"unique_section_name": {
"attribute": "my_attribute",
"prop": "my_prop",
"prop_list": [
"tests.config.test_section_serialization.CustomEncoder:class",
"tests.config.test_section_serialization.CustomDecoder:class"
]
},
"section_name": {
"default": {
"attribute": "default_attribute",
"prop": "default_prop",
"prop_int": "0:int"
},
"my_id": {
"attribute": "my_attribute",
"prop": "default_prop",
"prop_int": "0:int",
"prop_fct_list": [
"tests.config.test_section_serialization.add:function"
],
"prop_class_list": [
"tests.config.test_section_serialization.CustomClass:class"
]
},
"my_id_2": {
"attribute": "my_attribute_2",
"prop": "default_prop",
"prop_int": "0:int",
"prop_fct_list": [
"builtins.print:function",
"builtins.pow:function"
]
}
}
}
    """.strip()

    Config._serializer = _JsonSerializer()
    tf = NamedTemporaryFile()
    Config.configure_unique_section_for_tests(
        attribute="my_attribute",
        prop="my_prop",
        prop_list=[CustomEncoder, CustomDecoder],
    )
    Config.configure_section_for_tests(
        "my_id",
        "my_attribute",
        prop_fct_list=[add],
        prop_class_list=[CustomClass],
    )
    Config.configure_section_for_tests(
        "my_id_2",
        "my_attribute_2",
        prop_fct_list=[print, pow],
    )

    Config.backup(tf.filename)
    actual_exported_json = tf.read().strip()
    assert actual_exported_json == expected_json_config

    Config.override(tf.filename)
    tf2 = NamedTemporaryFile()
    Config.backup(tf2.filename)

    actual_exported_json_2 = tf2.read().strip()
    assert actual_exported_json_2 == expected_json_config
