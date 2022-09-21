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

from .config import Config

# Default config loaded by app.py
default_config: Config = {
    "port": 5000,
    "dark_mode": True,
    "debug": False,
    "host": "127.0.0.1",
    "use_reloader": False,
    "time_zone": None,
    "propagate": True,
    "favicon": None,
    "title": None,
    "theme": None,
    "light_theme": None,
    "dark_theme": None,
    "use_arrow": False,
    "system_notification": False,
    "notification_duration": 3000,
    "single_client": False,
    "ngrok_token": "",
    "upload_folder": None,
    "flask_log": False,
    "margin": "1em",
    "run_browser": True,
    "watermark": "Taipy inside",
    "change_delay": None,
    "extended_status": False,
}
