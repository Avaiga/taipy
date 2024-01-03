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

from .config import Config, Stylekit

_default_stylekit: Stylekit = {
    # Primary and secondary colors
    "color_primary": "#ff6049",
    "color_secondary": "#293ee7",
    # Contextual color
    "color_error": "#FF595E",
    "color_warning": "#FAA916",
    "color_success": "#96E6B3",
    # Background and elevation color for LIGHT MODE
    "color_background_light": "#f0f5f7",
    "color_paper_light": "#ffffff",
    # Background and elevation color for DARK MODE
    "color_background_dark": "#152335",
    "color_paper_dark": "#1f2f44",
    # DEFINING FONTS
    # Set main font family
    "font_family": "Lato, Arial, sans-serif",
    # DEFINING ROOT STYLES
    # Set root margin
    "root_margin": "1rem",
    # DEFINING SHAPES
    # Base border radius in px
    "border_radius": 8,
    # DEFINING MUI COMPONENTS STYLES
    # Matching input and button height in css size unit
    "input_button_height": "48px",
}

# Default config loaded by app.py
default_config: Config = {
    "allow_unsafe_werkzeug": False,
    "async_mode": "gevent",
    "change_delay": None,
    "chart_dark_template": None,
    "base_url": "/",
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
    "notebook_proxy": True,
    "notification_duration": 3000,
    "propagate": True,
    "run_browser": True,
    "run_in_thread": False,
    "run_server": True,
    "server_config": None,
    "single_client": False,
    "system_notification": False,
    "theme": None,
    "time_zone": None,
    "title": None,
    "stylekit": _default_stylekit.copy(),
    "upload_folder": None,
    "use_arrow": False,
    "use_reloader": False,
    "watermark": "Taipy inside",
    "webapp_path": None,
    "port": 5000,
}
