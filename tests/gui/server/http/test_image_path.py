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

import pathlib

from taipy.gui import Gui


def test_image_path_not_found(gui: Gui, helpers):
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.get(f"/taipy-images/images/img.png?client_id={sid}")
    assert ret.status_code == 404


def test_image_path_found(gui: Gui, helpers):
    url = gui._get_content(
        "img", str((pathlib.Path(__file__).parent.parent.parent / "resources" / "fred.png").resolve()), True
    )
    gui.run(run_server=False)
    flask_client = gui._server.test_client()
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    sid = helpers.create_scope_and_get_sid(gui)
    ret = flask_client.get(f"{url}?client_id={sid}")
    assert ret.status_code == 200


def test_image_data_too_big(gui: Gui, helpers):
    with open((pathlib.Path(__file__).parent.parent.parent / "resources" / "taipan.jpg"), "rb") as big_file:
        url = gui._get_content("img", big_file.read(), True)
        assert not url.startswith("data:")
