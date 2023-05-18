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

from cookiecutter.main import cookiecutter

from src.taipy._cli._scaffold_cli import _ScaffoldCLI


def test_create_call_to_cookiecutter():
    assert os.path.exists(_ScaffoldCLI._TEMPLATE_MAP["default"])
    assert os.listdir(_ScaffoldCLI._TEMPLATE_MAP["default"]) == [
        "cookiecutter.json",
        "{{cookiecutter.application_name}}",
    ]


def test_static_and_templates(tmpdir):
    cookiecutter(
        template=_ScaffoldCLI._TEMPLATE_MAP["default"],
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "application_name": "foo_app",
            "application_main_file": "main.py",
            "application_title": "bar",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert os.listdir(os.path.join(tmpdir, "foo_app")).sort() == ["requirements.txt", "main.py", "images"].sort()
