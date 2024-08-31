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

import os

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

from .utils import _run_template


def test_default_answer(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
    )

    assert os.listdir(tmpdir) == ["taipy_application"]
    assert sorted(os.listdir(os.path.join(tmpdir, "taipy_application"))) == sorted(["requirements.txt", "main.py"])

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "taipy_application"), "main.py")

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in stdout


def test_main_file_with_and_without_extension(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application main Python file": "app.py",
        },
    )
    assert sorted(os.listdir(os.path.join(tmpdir, "taipy_application"))) == sorted(["requirements.txt", "app.py"])

    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Application main Python file": "app",
        },
    )
    assert sorted(os.listdir(os.path.join(tmpdir, "foo_app"))) == sorted(["requirements.txt", "app.py"])


def test_with_orchestrator_service(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Does the application use scenario management or version management?": "y",
            "Does the application use Rest API?": "no",
        },
    )

    assert sorted(os.listdir(os.path.join(tmpdir, "taipy_application"))) == sorted(
        ["requirements.txt", "main.py", "configuration", "algorithms"]
    )
    with open(os.path.join(tmpdir, "taipy_application", "main.py")) as main_file:
        assert "orchestrator = Orchestrator()" in main_file.read()

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "taipy_application"), "main.py")

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in stdout
    assert "[Taipy][INFO] Development mode: " in stdout


def test_with_rest_service(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Does the application use scenario management or version management?": "n",
            "Does the application use Rest API?": "yes",
        },
    )

    assert sorted(os.listdir(os.path.join(tmpdir, "taipy_application"))) == sorted(["requirements.txt", "main.py"])
    with open(os.path.join(tmpdir, "taipy_application", "main.py")) as main_file:
        assert "rest = Rest()" in main_file.read()

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "taipy_application"), "main.py")

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in stdout
    assert "[Taipy][INFO] Development mode: " in stdout


def test_with_both_orchestrator_rest_services(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Does the application use scenario management or version management?": "y",
            "Does the application use Rest API?": "yes",
        },
    )

    assert sorted(os.listdir(os.path.join(tmpdir, "taipy_application"))) == sorted(
        ["requirements.txt", "main.py", "configuration", "algorithms"]
    )
    with open(os.path.join(tmpdir, "taipy_application", "main.py")) as main_file:
        assert "rest = Rest()" in main_file.read()
        assert "orchestrator = Orchestrator()" not in main_file.read()

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "taipy_application"), "main.py")

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in stdout
    assert "[Taipy][INFO] Development mode: " in stdout


def test_multipage_gui_template(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Page names in multi-page application?": "name_1 name_2 name_3",
        },
    )

    assert sorted(os.listdir(os.path.join(tmpdir, "foo_app"))) == sorted(["requirements.txt", "main.py", "pages"])
    assert sorted(os.listdir(os.path.join(tmpdir, "foo_app", "pages"))) == sorted(
        ["name_1", "name_2", "name_3", "root.md", "root.py", "__init__.py"]
    )

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "foo_app"), "main.py")
    assert "[Taipy][INFO]  * Server starting on" in stdout


def test_multipage_gui_template_with_invalid_page_name(tmpdir, capfd):
    with pytest.raises(FailedHookException):
        cookiecutter(
            template="taipy/templates/default",
            output_dir=str(tmpdir),
            no_input=True,
            extra_context={
                "Application root folder name": "foo_app",
                "Page names in multi-page application?": "valid_var_name 1_invalid_var_name",
            },
        )

    _, stderr = capfd.readouterr()
    assert 'Page name "1_invalid_var_name" is not a valid Python identifier' in stderr

    assert not os.path.exists(os.path.join(tmpdir, "foo_app"))


def test_with_git(tmpdir):
    cookiecutter(
        template="taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Do you want to initialize a new Git repository?": "y",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert sorted(os.listdir(os.path.join(tmpdir, "foo_app"))) == sorted(
        ["requirements.txt", "main.py", ".git", ".gitignore"]
    )
