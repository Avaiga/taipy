import argparse
import os
import re
import typing as t
import warnings

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
    "client_url",
    "favicon",
    "title",
    "theme",
    "theme[light]",
    "theme[dark]",
    "use_arrow",
    "browser_notification",
    "notification_duration",
    "single_client",
    "ngrok_token",
    "upload_folder",
    "data_url_max_size",
    "flask_log",
    "margin",
]

Config = t.TypedDict(
    "AppConfig",
    {
        "port": int,
        "dark_mode": bool,
        "debug": bool,
        "host": str,
        "use_reloader": bool,
        "time_zone": str,
        "propagate": bool,
        "client_url": str,
        "favicon": t.Union[str, None],
        "title": t.Union[str, None],
        "theme": t.Union[t.Dict[str, t.Any], None],
        "theme[light]": t.Union[t.Dict[str, t.Any], None],
        "theme[dark]": t.Union[t.Dict[str, t.Any], None],
        "use_arrow": bool,
        "browser_notification": bool,
        "notification_duration": int,
        "single_client": bool,
        "ngrok_token": str,
        "upload_folder": t.Union[str, None],
        "data_url_max_size": t.Union[int, None],
        "flask_log": bool,
        "margin": t.Union[str, None],
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

    def get_time_zone(self) -> str:
        if "time_zone" not in self.config or self.config["time_zone"] == "client":
            return "client"
        if self.config["time_zone"] == "server":
            # return python tzlocal IANA Time Zone
            return str(tzlocal.get_localzone())
        # Verify user defined IANA Time Zone is valid
        if self.config["time_zone"] not in pytz.all_timezones_set:
            raise Exception(
                "Time Zone configuration is not valid. Mistyped 'server', 'client' options or invalid IANA Time Zone"
            )
        # return user defined IANA Time Zone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
        return self.config["time_zone"]

    def _init_argparse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-P", "--port", nargs="?", default="", const="", help="Specify server port")
        parser.add_argument("-H", "--host", nargs="?", default="", const="", help="Specify server host")
        parser.add_argument(
            "-C", "--client-url", nargs="?", default="", const="", help="Specify backend endpoint on client side"
        )

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
        if args.client_url:
            config["client_url"] = args.client_url
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
        if os.path.isfile(env_file_abs_path):
            for key, value in dotenv_values(env_file_abs_path).items():
                key = key.lower()
                if value is not None and key in config:
                    try:
                        config[key] = (value if config[key] is None else type(config[key])(value))  # type: ignore
                    except Exception as e:
                        warnings.warn(
                            f"Invalid env value in Gui.run: {key} - {value}. Unable to parse value to the correct type.\n{e}"
                        )
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
        # Load from system arguments
        self._init_argparse()
