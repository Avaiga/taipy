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

import argparse
import os
import re
import typing as t
import warnings
from importlib.util import find_spec

import pytz
import tzlocal
from dotenv import dotenv_values

from ._page import _Page
from .partial import Partial

ConfigParameter = t.Literal[
    "port",
    "dark_mode",
    "debug",
    "host",
    "use_reloader",
    "time_zone",
    "propagate",
    "favicon",
    "title",
    "theme",
    "light_theme",
    "dark_theme",
    "use_arrow",
    "system_notification",
    "notification_duration",
    "single_client",
    "ngrok_token",
    "upload_folder",
    "data_url_max_size",
    "flask_log",
    "margin",
    "run_browser",
    "watermark",
    "change_delay",
    "extended_status",
]

Config = t.TypedDict(
    "Config",
    {
        "port": int,
        "dark_mode": bool,
        "debug": bool,
        "host": str,
        "use_reloader": bool,
        "time_zone": t.Union[str, None],
        "propagate": bool,
        "favicon": t.Union[str, None],
        "title": t.Union[str, None],
        "theme": t.Union[t.Dict[str, t.Any], None],
        "light_theme": t.Union[t.Dict[str, t.Any], None],
        "dark_theme": t.Union[t.Dict[str, t.Any], None],
        "use_arrow": bool,
        "system_notification": bool,
        "notification_duration": int,
        "single_client": bool,
        "ngrok_token": str,
        "upload_folder": t.Union[str, None],
        "data_url_max_size": t.Union[int, None],
        "flask_log": bool,
        "margin": t.Union[str, None],
        "run_browser": bool,
        "watermark": t.Union[str, None],
        "change_delay": t.Union[int, None],
        "extended_status": bool,
    },
    total=False,
)


class _Config(object):

    __RE_PORT_NUMBER = re.compile(
        r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
    )

    def __init__(self):
        self.pages: t.List[_Page] = []
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
                    warnings.warn(
                        f'app_config "{name}" value "{self.config[name]}" is not of type {type(default_value)}\n{e}'
                    )
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

    def _init_argparse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-P", "--port", nargs="?", default="", const="", help="Specify server port")
        parser.add_argument("-H", "--host", nargs="?", default="", const="", help="Specify server host")

        parser.add_argument("--ngrok-token", nargs="?", default="", const="", help="Specify NGROK Authtoken")

        debug_group = parser.add_mutually_exclusive_group()
        debug_group.add_argument("--debug", help="Turn on debug", action="store_true")
        debug_group.add_argument("--no-debug", help="Turn off debug", action="store_true")

        reloader_group = parser.add_mutually_exclusive_group()
        reloader_group.add_argument("--use-reloader", help="Auto reload on code changes", action="store_true")
        reloader_group.add_argument("--no-reloader", help="No reload on code changes", action="store_true")

        args, unknown_args = parser.parse_known_args()
        self._handle_argparse(args)

    def _handle_argparse(self, args):  # pragma: no cover
        config = self.config
        if args.port:
            if not _Config.__RE_PORT_NUMBER.match(args.port):
                warnings.warn("Port value for --port option is not valid")
            else:
                config["port"] = int(args.port)
        if args.host:
            config["host"] = args.host
        if args.debug:
            config["debug"] = True
        if args.no_debug:
            config["debug"] = False
        if args.use_reloader:
            config["use_reloader"] = True
        if args.no_reloader:
            config["use_reloader"] = False
        if args.ngrok_token:
            config["ngrok_token"] = args.ngrok_token

    def _build_config(self, root_dir, env_filename, kwargs):  # pragma: no cover
        config = self.config
        env_file_abs_path = env_filename if os.path.isabs(env_filename) else os.path.join(root_dir, env_filename)
        # Load keyword arguments
        for key, value in kwargs.items():
            key = key.lower()
            if value is not None and key in config:
                try:
                    config[key] = value if config[key] is None else type(config[key])(value)  # type: ignore
                except Exception as e:
                    warnings.warn(
                        f"Invalid keyword arguments value in Gui.run {key} - {value}. Unable to parse value to the correct type.\n{e}"
                    )
        # Load config from env file
        if os.path.isfile(env_file_abs_path):
            for key, value in dotenv_values(env_file_abs_path).items():
                key = key.lower()
                if value is not None and key in config:
                    try:
                        config[key] = value if config[key] is None else type(config[key])(value)  # type: ignore
                    except Exception as e:
                        warnings.warn(
                            f"Invalid env value in Gui.run: {key} - {value}. Unable to parse value to the correct type.\n{e}"
                        )
        # Load from system arguments
        self._init_argparse()

        # Taipy-config
        if find_spec("taipy") and find_spec("taipy.config"):
            from taipy.config import Config as TaipyConfig

            try:
                section = TaipyConfig.unique_sections["gui"]
                self.config.update(section._to_dict())
            except KeyError:
                warnings.warn("taipy-config section for taipy-gui is not initialized")


def _register_gui_config():
    if not find_spec("taipy") or not find_spec("taipy.config"):
        return
    from copy import copy

    from taipy.config import Config as TaipyConfig
    from taipy.config import UniqueSection

    from ._default_config import default_config

    class _GuiSection(UniqueSection):

        name = "gui"

        def __init__(self, property_list: t.Optional[t.List] = None, **properties):
            self._property_list = property_list
            super().__init__(**properties)

        def __copy__(self):
            return _GuiSection(property_list=copy(self._property_list), **copy(self._properties))

        def _to_dict(self):
            as_dict = {}
            as_dict.update(self._properties)
            return as_dict

        @classmethod
        def _from_dict(cls, as_dict: t.Dict[str, t.Any], *_):
            return _GuiSection(property_list=list(default_config), **as_dict)

        def _update(self, as_dict: t.Dict[str, t.Any]):
            if self._property_list:
                as_dict = {k: v for k, v in as_dict.items() if k in self._property_list}
            self._properties.update(as_dict)

        @staticmethod
        def _configure(**properties):
            section = _GuiSection(property_list=list(default_config), **properties)
            TaipyConfig._register(section)
            return TaipyConfig.unique_sections[_GuiSection.name]

    TaipyConfig._register_default(_GuiSection(property_list=list(default_config)))
    TaipyConfig.configure_gui = _GuiSection._configure
