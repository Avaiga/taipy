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

import argparse

import pytest

from src.taipy.config.common._argparser import _Argparser


@pytest.fixture(autouse=True, scope="function")
def clean_argparser():
    _Argparser.parser = argparse.ArgumentParser(conflict_handler="resolve")
    _Argparser.arg_groups = {}

    yield


def test_parser(capfd):
    group_1 = _Argparser._add_groupparser("group_1", "group_1 desc")
    group_1.add_argument("--foo", "-f", help="foo help")
    group_1.add_argument("--bar", "-b", help="bar help")

    group_2 = _Argparser._add_groupparser("group_2", "group_2 desc")
    group_2.add_argument("--doo", "-d", help="doo help")
    group_2.add_argument("--baz", "-z", help="baz help")

    expected_help_message = """
group_1:
  group_1 desc

  --foo FOO, -f FOO  foo help
  --bar BAR, -b BAR  bar help

group_2:
  group_2 desc

  --doo DOO, -d DOO  doo help
  --baz BAZ, -z BAZ  baz help
    """.strip()

    _Argparser.parser.print_help()
    stdout, _ = capfd.readouterr()

    assert expected_help_message in stdout


def test_duplicate_group(capfd):
    group_1 = _Argparser._add_groupparser("group_1", "group_1 desc")
    group_1.add_argument("--foo", "-f", help="foo help")

    group_2 = _Argparser._add_groupparser("group_1", "group_2 desc")
    group_2.add_argument("--bar", "-b", help="bar help")

    # The title of group_2 is duplicated with  group_1, and therefore
    # there will be no new group created
    assert len(_Argparser.arg_groups) == 1
