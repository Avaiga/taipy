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

import os

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

from .utils import _run_template


def test_default_answer(tmpdir):
    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
    )

    assert os.listdir(tmpdir) == ["taipy_application"]
    assert (
        os.listdir(os.path.join(tmpdir, "taipy_application")).sort() == ["requirements.txt", "main.py", "images"].sort()
    )
    with open(os.path.join(tmpdir, "taipy_application", "requirements.txt")) as requirements_file:
        # Assert post_gen_project hook is successful
        assert "taipy==" in requirements_file.read()

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "taipy_application"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")


def test_main_file_with_and_without_extension(tmpdir):
    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application main Python file": "app.py",
        },
    )
    assert (
        os.listdir(os.path.join(tmpdir, "taipy_application")).sort() == ["requirements.txt", "app.py", "images"].sort()
    )

    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Application main Python file": "app",
        },
    )
    assert os.listdir(os.path.join(tmpdir, "foo_app")).sort() == ["requirements.txt", "app.py", "images"].sort()


def test_with_core_service(tmpdir):
    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Does the application use scenario management or version management?": "y",
            "Does the application use Rest API?": "no",
        },
    )

    assert (
        os.listdir(os.path.join(tmpdir, "taipy_application")).sort()
        == ["requirements.txt", "main.py", "images", "configuration", "algorithms"].sort()
    )
    with open(os.path.join(tmpdir, "taipy_application", "main.py")) as main_file:
        assert "core = Core()" in main_file.read()

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "taipy_application"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")
    assert "[Taipy][INFO] Development mode: " in str(stdout, "utf-8")


def test_with_rest_service(tmpdir):
    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Does the application use scenario management or version management?": "n",
            "Does the application use Rest API?": "yes",
        },
    )

    assert (
        os.listdir(os.path.join(tmpdir, "taipy_application")).sort() == ["requirements.txt", "main.py", "images"].sort()
    )
    with open(os.path.join(tmpdir, "taipy_application", "main.py")) as main_file:
        assert "rest = Rest()" in main_file.read()

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "taipy_application"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")
    assert "[Taipy][INFO] Development mode: " in str(stdout, "utf-8")


def test_with_both_core_rest_services(tmpdir):
    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Does the application use scenario management or version management?": "n",
            "Does the application use Rest API?": "yes",
        },
    )

    assert (
        os.listdir(os.path.join(tmpdir, "taipy_application")).sort()
        == ["requirements.txt", "main.py", "images", "configuration", "algorithms"].sort()
    )
    with open(os.path.join(tmpdir, "taipy_application", "main.py")) as main_file:
        assert "rest = Rest()" in main_file.read()
        assert "core = Core()" not in main_file.read()

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "taipy_application"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")
    assert "[Taipy][INFO] Development mode: " in str(stdout, "utf-8")


def test_multipage_gui_template(tmpdir):
    cookiecutter(
        template="src/taipy/templates/default",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Page names in multi-page application?": "name_1 name_2 name_3",
        },
    )

    assert (
        os.listdir(os.path.join(tmpdir, "foo_app")).sort() == ["requirements.txt", "main.py", "pages", "images"].sort()
    )
    assert (
        os.listdir(os.path.join(tmpdir, "foo_app", "pages")).sort()
        == ["name_1", "name_2", "name_3", "root.md", "root.py", "__init__.py"].sort()
    )

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "foo_app"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")


def test_multipage_gui_template_with_invalid_page_name(tmpdir, capfd):
    with pytest.raises(FailedHookException):
        cookiecutter(
            template="src/taipy/templates/default",
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
