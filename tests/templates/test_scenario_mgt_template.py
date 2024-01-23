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

from cookiecutter.main import cookiecutter

from .utils import _run_template


def test_scenario_management_with_toml_config(tmpdir):
    cookiecutter(
        template="taipy/templates/scenario-management",
        output_dir=tmpdir,
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Application main Python file": "main.py",
            "Application title": "bar",
            "Does the application use TOML Config?": "yes",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert (
        os.listdir(os.path.join(tmpdir, "foo_app")).sort()
        == ["requirements.txt", "main.py", "algos", "config", "pages"].sort()
    )

    assert (
        os.listdir(os.path.join(tmpdir, "foo_app", "config")).sort()
        == ["__init__.py", "config.py", "config.toml"].sort()
    )
    with open(os.path.join(tmpdir, "foo_app", "config", "config.py")) as config_file:
        assert 'Config.load("config/config.toml")' in config_file.read()

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "foo_app"), "main.py")

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO] Configuration 'config/config.toml' successfully loaded." in stdout
    assert "[Taipy][INFO]  * Server starting on" in stdout


def test_scenario_management_without_toml_config(tmpdir):
    cookiecutter(
        template="taipy/templates/scenario-management",
        output_dir=tmpdir,
        no_input=True,
        extra_context={
            "Application root folder name": "foo_app",
            "Application main Python file": "main.py",
            "Application title": "bar",
            "Does the application use TOML Config?": "no",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert (
        os.listdir(os.path.join(tmpdir, "foo_app")).sort()
        == ["requirements.txt", "main.py", "algos", "config", "pages"].sort()
    )

    assert os.listdir(os.path.join(tmpdir, "foo_app", "config")).sort() == ["__init__.py", "config.py"].sort()
    with open(os.path.join(tmpdir, "foo_app", "config", "config.py")) as config_file:
        config_content = config_file.read()
        assert 'Config.load("config/config.toml")' not in config_content
        assert all(x in config_content for x in ["Config.configure_csv_data_node", "Config.configure_task"])

    taipy_path = os.getcwd()
    stdout = _run_template(taipy_path, os.path.join(tmpdir, "foo_app"), "main.py")

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in stdout
