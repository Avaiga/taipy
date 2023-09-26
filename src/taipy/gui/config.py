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
import re
import typing as t
from importlib.util import find_spec

import pytz
import tzlocal
from dotenv import dotenv_values
from werkzeug.serving import is_running_from_reloader

from taipy.logger._taipy_logger import _TaipyLogger

from ._gui_cli import _GuiCLI
from ._page import _Page
from ._warnings import _warn
from .partial import Partial
from .utils import _is_in_notebook

ConfigParameter = t.Literal[
    "allow_unsafe_werkzeug",
    "async_mode",
    "change_delay",
    "chart_dark_template",
    "base_url",
    "dark_mode",
    "dark_theme",
    "data_url_max_size",
    "debug",
    "extended_status",
    "favicon",
    "flask_log",
    "host",
    "light_theme",
    "margin",
    "ngrok_token",
    "notebook_proxy",
    "notification_duration",
    "propagate",
    "run_browser",
    "run_in_thread",
    "run_server",
    "server_config",
    "single_client",
    "system_notification",
    "theme",
    "time_zone",
    "title",
    "stylekit",
    "upload_folder",
    "use_arrow",
    "use_reloader",
    "watermark",
    "webapp_path",
    "port",
]

Stylekit = t.TypedDict(
    "Stylekit",
    {
        "color_primary": str,
        "color_secondary": str,
        "color_error": str,
        "color_warning": str,
        "color_success": str,
        "color_background_light": str,
        "color_paper_light": str,
        "color_background_dark": str,
        "color_paper_dark": str,
        "font_family": str,
        "root_margin": str,
        "border_radius": int,
        "input_button_height": str,
    },
    total=False,
)

ServerConfig = t.TypedDict(
    "ServerConfig",
    {
        "cors": t.Optional[t.Union[bool, t.Dict[str, t.Any]]],
        "socketio": t.Optional[t.Dict[str, t.Any]],
        "ssl_context": t.Optional[t.Union[str, t.Tuple[str, str]]],
        "flask": t.Optional[t.Dict[str, t.Any]],
    },
    total=False,
)

Config = t.TypedDict(
    "Config",
    {
        "allow_unsafe_werkzeug": bool,
        "async_mode": str,
        "change_delay": t.Optional[int],
        "chart_dark_template": t.Optional[t.Dict[str, t.Any]],
        "base_url": t.Optional[str],
        "dark_mode": bool,
        "dark_theme": t.Optional[t.Dict[str, t.Any]],
        "data_url_max_size": t.Optional[int],
        "debug": bool,
        "extended_status": bool,
        "favicon": t.Optional[str],
        "flask_log": bool,
        "host": str,
        "light_theme": t.Optional[t.Dict[str, t.Any]],
        "margin": t.Optional[str],
        "ngrok_token": str,
        "notebook_proxy": bool,
        "notification_duration": int,
        "propagate": bool,
        "run_browser": bool,
        "run_in_thread": bool,
        "run_server": bool,
        "server_config": t.Optional[ServerConfig],
        "single_client": bool,
        "system_notification": bool,
        "theme": t.Optional[t.Dict[str, t.Any]],
        "time_zone": t.Optional[str],
        "title": t.Optional[str],
        "stylekit": t.Union[bool, Stylekit],
        "upload_folder": t.Optional[str],
        "use_arrow": bool,
        "use_reloader": bool,
        "watermark": t.Optional[str],
        "webapp_path": t.Optional[str],
        "port": int,
    },
    total=False,
)


class _Config(object):
    __RE_PORT_NUMBER = re.compile(
        r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
    )

    def __init__(self):
        self.pages: t.List[_Page] = []
        self.root_page: t.Optional[_Page] = None
        self.routes: t.List[str] = []
        self.partials: t.List[Partial] = []
        self.partial_routes: t.List[str] = []
        self.config: Config = {}

    def _load(self, config: Config) -> None:
        self.config.update(config)
        # Check that the user timezone configuration setting is valid
        self.get_time_zone()

    def _get_config(self, name: ConfigParameter, default_value: t.Any) -> t.Any:  # pragma: no cover
        if name in self.config and self.config[name] is not None:
            if default_value is not None and not isinstance(self.config[name], type(default_value)):
                try:
                    return type(default_value)(self.config[name])
                except Exception as e:
                    _warn(f'app_config "{name}" value "{self.config[name]}" is not of type {type(default_value)}', e)
                    return default_value
            return self.config[name]
        return default_value

    def get_time_zone(self) -> t.Optional[str]:
        tz = self.config.get("time_zone")
        if tz is None or tz == "client":
            return tz
        if tz == "server":
            # return python tzlocal IANA Time Zone
            return str(tzlocal.get_localzone())
        # Verify user defined IANA Time Zone is valid
        if tz not in pytz.all_timezones_set:
            raise Exception(
                "Time Zone configuration is not valid. Mistyped 'server', 'client' options or invalid IANA Time Zone"
            )
        # return user defined IANA Time Zone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
        return tz

    def _handle_argparse(self):
        _GuiCLI.create_parser()
        args = _GuiCLI.parse_arguments()

        config = self.config
        if args.taipy_port:
            if not _Config.__RE_PORT_NUMBER.match(args.taipy_port):
                _warn("Port value for --port option is not valid.")
            else:
                config["port"] = int(args.taipy_port)
        if args.taipy_host:
            config["host"] = args.taipy_host
        if args.taipy_debug:
            config["debug"] = True
        if args.taipy_no_debug:
            config["debug"] = False
        if args.taipy_use_reloader:
            config["use_reloader"] = True
        if args.taipy_no_reloader:
            config["use_reloader"] = False
        if args.taipy_ngrok_token:
            config["ngrok_token"] = args.taipy_ngrok_token
        if args.taipy_webapp_path:
            config["webapp_path"] = args.taipy_webapp_path
        elif os.environ.get("TAIPY_GUI_WEBAPP_PATH"):
            config["webapp_path"] = os.environ.get("TAIPY_GUI_WEBAPP_PATH")

    def _build_config(self, root_dir, env_filename, kwargs):  # pragma: no cover
        config = self.config
        env_file_abs_path = env_filename if os.path.isabs(env_filename) else os.path.join(root_dir, env_filename)
        # Load keyword arguments
        for key, value in kwargs.items():
            key = key.lower()
            if value is not None and key in config:
                # Special case for "stylekit" that can be a Boolean or a dict
                if key == "stylekit" and isinstance(value, bool):
                    from ._default_config import _default_stylekit

                    config[key] = _default_stylekit if value else {}
                    continue
                try:
                    if isinstance(value, dict) and isinstance(config[key], dict):
                        config[key].update(value)
                    else:
                        config[key] = value if config[key] is None else type(config[key])(value)  # type: ignore
                except Exception as e:
                    _warn(
                        f"Invalid keyword arguments value in Gui.run {key} - {value}. Unable to parse value to the correct type",
                        e,
                    )
        # Load config from env file
        if os.path.isfile(env_file_abs_path):
            for key, value in dotenv_values(env_file_abs_path).items():
                key = key.lower()
                if value is not None and key in config:
                    try:
                        config[key] = value if config[key] is None else type(config[key])(value)  # type: ignore
                    except Exception as e:
                        _warn(
                            f"Invalid env value in Gui.run(): {key} - {value}. Unable to parse value to the correct type",
                            e,
                        )

        # Taipy-config
        if find_spec("taipy") and find_spec("taipy.config"):
            from taipy.config import Config as TaipyConfig

            try:
                section = TaipyConfig.unique_sections["gui"]
                self.config.update(section._to_dict())
            except KeyError:
                _warn("taipy-config section for taipy-gui is not initialized.")

        # Load from system arguments
        self._handle_argparse()

    def __log_outside_reloader(self, logger, msg):
        if not is_running_from_reloader():
            logger.info(msg)

    def resolve(self):
        app_config = self.config
        logger = _TaipyLogger._get_logger()
        # Special config for notebook runtime
        if _is_in_notebook() or app_config["run_in_thread"] and not app_config["single_client"]:
            app_config["single_client"] = True
            self.__log_outside_reloader(logger, "Running in 'single_client' mode in notebook environment")

        if app_config["run_server"] and app_config["ngrok_token"] and app_config["use_reloader"]:
            app_config["use_reloader"] = False
            self.__log_outside_reloader(
                logger, "'use_reloader' parameter will not be used when 'ngrok_token' parameter is available"
            )

        if app_config["use_reloader"] and _is_in_notebook():
            app_config["use_reloader"] = False
            self.__log_outside_reloader(logger, "'use_reloader' parameter is not available in notebook environment")

        if app_config["use_reloader"] and not app_config["debug"]:
            app_config["debug"] = True
            self.__log_outside_reloader(logger, "application is running in 'debug' mode")

        if app_config["debug"] and not app_config["allow_unsafe_werkzeug"]:
            app_config["allow_unsafe_werkzeug"] = True
            self.__log_outside_reloader(logger, "'allow_unsafe_werkzeug' has been set to True")

        if app_config["debug"] and app_config["async_mode"] != "threading":
            app_config["async_mode"] = "threading"
            self.__log_outside_reloader(
                logger,
                "'async_mode' parameter has been overridden to 'threading'. Using Flask built-in development server with debug mode",
            )

        self._resolve_notebook_proxy()
        self._resolve_stylekit()
        self._resolve_url_prefix()

    def _resolve_stylekit(self):
        app_config = self.config
        # support legacy margin variable
        stylekit_config = app_config["stylekit"]

        if isinstance(app_config["stylekit"], dict) and "root_margin" in app_config["stylekit"]:
            from ._default_config import _default_stylekit, default_config

            stylekit_config = app_config["stylekit"]
            if (
                stylekit_config["root_margin"] == _default_stylekit["root_margin"]
                and app_config["margin"] != default_config["margin"]
            ):
                app_config["stylekit"]["root_margin"] = str(app_config["margin"])
            app_config["margin"] = None

    def _resolve_url_prefix(self):
        app_config = self.config
        base_url = app_config.get("base_url")
        if base_url is None:
            app_config["base_url"] = "/"
        else:
            base_url = f"{'' if base_url.startswith('/') else '/'}{base_url}"
            base_url = f"{base_url}{'' if base_url.endswith('/') else '/'}"
            app_config["base_url"] = base_url

    def _resolve_notebook_proxy(self):
        app_config = self.config
        app_config["notebook_proxy"] = app_config["notebook_proxy"] if _is_in_notebook() else False
