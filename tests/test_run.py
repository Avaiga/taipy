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

from unittest import mock

from taipy._run import _run
from taipy.core import Orchestrator
from taipy.gui import Gui
from taipy.rest import Rest


@mock.patch("taipy.gui.Gui.run")
def test_run_pass_with_gui(gui_run):
    _run(Gui())
    gui_run.assert_called_once()


@mock.patch("taipy.core.Orchestrator.run")
def test_run_pass_with_core(orchestrator_run):
    _run(Orchestrator())
    orchestrator_run.assert_called_once()


@mock.patch("taipy.rest.Rest.run")
@mock.patch("taipy.core.Orchestrator.run")
def test_run_pass_with_rest(rest_run, orchestrator_run):
    _run(Rest())
    rest_run.assert_called_once()
    orchestrator_run.assert_called_once()


@mock.patch("taipy.rest.Rest.run")
@mock.patch("taipy.core.Orchestrator.run")
def test_run_pass_with_core_and_rest(orchestrator_run, rest_run):
    _run(Orchestrator(), Rest())
    orchestrator_run.assert_called_once()
    rest_run.assert_called_once()


@mock.patch("taipy.gui.Gui.run")
@mock.patch("taipy.rest.Rest.run")
@mock.patch("taipy.core.Orchestrator.run")
def test_run_pass_with_gui_and_rest(orchestrator_run, rest_run, gui_run):
    _run(Gui(), Rest())
    gui_run.assert_called_once()
    orchestrator_run.assert_called_once()
    rest_run.assert_not_called()


@mock.patch("taipy.gui.Gui.run")
@mock.patch("taipy.core.Orchestrator.run")
def test_run_pass_with_gui_and_core(orchestrator_run, gui_run):
    _run(Gui(), Orchestrator())
    gui_run.assert_called_once()
    orchestrator_run.assert_called_once()
