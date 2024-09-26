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

import re
import sys

from taipy.common._cli._base_cli._taipy_parser import _TaipyParser

if sys.version_info >= (3, 10):
    argparse_options_str = "options:"
else:
    argparse_options_str = "optional arguments:"


def preprocess_stdout(stdout):
    stdout = stdout.replace("\n", " ").replace("\t", " ")
    return re.sub(" +", " ", stdout)


def test_subparser(capfd):
    subcommand_1 = _TaipyParser._add_subparser("subcommand_1", help="subcommand_1 help")
    subcommand_1.add_argument("--foo", "-f", help="foo help")
    subcommand_1.add_argument("--bar", "-b", help="bar help")

    subcommand_2 = _TaipyParser._add_subparser("subcommand_2", help="subcommand_2 help")
    subcommand_2.add_argument("--doo", "-d", help="doo help")
    subcommand_2.add_argument("--baz", "-z", help="baz help")

    expected_subcommand_1_help_message = f"""subcommand_1 [-h] [--foo FOO] [--bar BAR]

{argparse_options_str}
  -h, --help         show this help message and exit
  --foo FOO, -f FOO  foo help
  --bar BAR, -b BAR  bar help
    """

    subcommand_1.print_help()
    stdout, _ = capfd.readouterr()
    assert preprocess_stdout(expected_subcommand_1_help_message) in preprocess_stdout(stdout)

    expected_subcommand_2_help_message = f"""subcommand_2 [-h] [--doo DOO] [--baz BAZ]

{argparse_options_str}
  -h, --help         show this help message and exit
  --doo DOO, -d DOO  doo help
  --baz BAZ, -z BAZ  baz help
    """

    subcommand_2.print_help()
    stdout, _ = capfd.readouterr()
    assert preprocess_stdout(expected_subcommand_2_help_message) in preprocess_stdout(stdout)


def test_duplicate_subcommand():
    subcommand_1 = _TaipyParser._add_subparser("subcommand_1", help="subcommand_1 help")
    subcommand_1.add_argument("--foo", "-f", help="foo help")

    subcommand_2 = _TaipyParser._add_subparser("subcommand_1", help="subcommand_2 help")
    subcommand_2.add_argument("--bar", "-b", help="bar help")

    # The title of subcommand_2 is duplicated with  subcommand_1, and therefore
    # there will be no new subcommand created
    assert len(_TaipyParser._sub_taipyparsers) == 1


def test_groupparser(capfd):
    group_1 = _TaipyParser._add_groupparser("group_1", "group_1 desc")
    group_1.add_argument("--foo", "-f", help="foo help")
    group_1.add_argument("--bar", "-b", help="bar help")

    group_2 = _TaipyParser._add_groupparser("group_2", "group_2 desc")
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

    _TaipyParser._parser.print_help()
    stdout, _ = capfd.readouterr()

    assert expected_help_message in stdout


def test_duplicate_group():
    group_1 = _TaipyParser._add_groupparser("group_1", "group_1 desc")
    group_1.add_argument("--foo", "-f", help="foo help")

    group_2 = _TaipyParser._add_groupparser("group_1", "group_2 desc")
    group_2.add_argument("--bar", "-b", help="bar help")

    # The title of group_2 is duplicated with  group_1, and therefore
    # there will be no new group created
    assert len(_TaipyParser._arg_groups) == 1
