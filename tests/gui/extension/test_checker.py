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
import os


def test_extension_checker(capsys):
    from taipy.gui.extension._main._check_extension import _check_extension

    saved_cwd = os.getcwd()

    # extlib_test has no front-end
    os.chdir(os.path.dirname(__file__))
    try:
        assert _check_extension("extlib_test") == 1  # expect failure
        captured = capsys.readouterr()
        assert "front-end: No front-end directory found" in captured.out
    finally:
        os.chdir(saved_cwd)

    # check1 has no issue
    os.chdir(os.path.dirname(__file__) + "/check1")
    try:
        failure = _check_extension("extlib1")
        captured = capsys.readouterr()
        assert not failure  # expect success
        assert "front-end: Found front-end" in captured.out
        assert "webpack.entry: Webpack entry point file not found" in captured.out
        assert "MANIFEST.include: Webpack output path" in captured.out
    finally:
        os.chdir(saved_cwd)

    # check2 has a fatal issue: library without get_name()
    os.chdir(os.path.dirname(__file__) + "/check2")
    try:
        failure = _check_extension("extlib2")
        captured = capsys.readouterr()
        assert failure  # expect failure
        assert "is missing get_name() implementation" in captured.out
    finally:
        os.chdir(saved_cwd)

    # check3 has a fatal issue: name mismatch with webpack library name
    os.chdir(os.path.dirname(__file__) + "/check3")
    try:
        failure = _check_extension("extlib3")
        captured = capsys.readouterr()
        assert failure  # expect failure
        assert "does not match the name derived" in captured.out
    finally:
        os.chdir(saved_cwd)
