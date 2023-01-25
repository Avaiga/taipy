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

from .config import Config


# Default config loaded by app.py
default_config: Config = {
    "allow_unsafe_werkzeug": False,
    "async_mode": "gevent",
    "change_delay": None,
    "chart_dark_template": None,
    "dark_mode": True,
    "dark_theme": None,
    "debug": False,
    "extended_status": False,
    "favicon": None,
    "flask_log": False,
    "host": "127.0.0.1",
    "light_theme": None,
    "margin": "1em",
    "ngrok_token": "",
    "notification_duration": 3000,
    "propagate": True,
    "run_browser": True,
    "run_in_thread": False,
    "run_server": True,
    "single_client": False,
    "system_notification": False,
    "theme": None,
    "time_zone": None,
    "title": None,
    "upload_folder": None,
    "use_arrow": False,
    "use_reloader": False,
    "watermark": "Taipy inside",
    "webapp_path": None,
    "port": 5000,
}
