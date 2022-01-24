import argparse
import os
import re
import typing as t
import warnings

import pytz
import tzlocal
from dotenv import dotenv_values

from .page import Page, Partial

AppConfigOption = t.Literal[
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
]

AppConfig = t.TypedDict(
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
    },
    total=False,
)

StyleConfig = t.TypedDict(
    "StyleConfig",
    {
        "button": str,
        "chart": str,
        "date_selector": str,
        "dialog": str,
        "expandable": str,
        "field": str,
        "file_download": str,
        "file_selector": str,
        "image": str,
        "input": str,
        "layout": str,
        "navbar": str,
        "pane": str,
        "part": str,
        "selector": str,
        "slider": str,
        "status": str,
        "table": str,
        "toggle": str,
        "tree": str,
    },
    total=False,
)


class GuiConfig(object):

    __RE_PORT_NUMBER = re.compile(
        r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
    )

    def __init__(self):
        self.pages: t.List[Page] = []
        self.routes: t.List[str] = []
        self.partials: t.List[Partial] = []
        self.partial_routes: t.List[str] = []
        self.app_config: AppConfig = {}
        self.style_config: StyleConfig = {}

    def load_config(self, app_config={}, style_config={}) -> None:
        self.app_config.update(app_config)
        self.style_config.update(style_config)
        # Run get_time_zone to verify user predefined IANA time_zone if available
        self.get_time_zone()

    def _get_app_config(self, name: AppConfigOption, default_value: t.Any) -> t.Any:
        if name in self.app_config and self.app_config[name] is not None:
            if default_value is not None and not isinstance(self.app_config[name], type(default_value)):
                try:
                    return type(default_value)(self.app_config[name])
                except Exception as e:
                    warnings.warn(
                        f'app_config "{name}" value "{self.app_config[name]}" is not of type {type(default_value)}\n{e}'
                    )
                    return default_value
            return self.app_config[name]
        return default_value

    def get_time_zone(self) -> str:
        if "time_zone" not in self.app_config or self.app_config["time_zone"] == "client":
            return "client"
        if self.app_config["time_zone"] == "server":
            # return python tzlocal IANA Time Zone
            return str(tzlocal.get_localzone())
        # Verify user defined IANA Time Zone is valid
        if self.app_config["time_zone"] not in pytz.all_timezones_set:
            raise Exception(
                "Time Zone configuration is not valid! Mistyped 'server', 'client' options of invalid IANA Time Zone!"
            )
        # return user defined IANA Time Zone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
        return self.app_config["time_zone"]

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

    def _handle_argparse(self, args):
        app_config = self.app_config
        if args.port:
            if not GuiConfig.__RE_PORT_NUMBER.match(args.port):
                warnings.warn("Port value for --port option is not valid")
            else:
                app_config["port"] = int(args.port)
        if args.host:
            app_config["host"] = args.host
        if args.client_url:
            app_config["client_url"] = args.client_url
        if args.debug:
            app_config["debug"] = True
        if args.no_debug:
            app_config["debug"] = False
        if args.use_reloader:
            app_config["use_reloader"] = True
        if args.no_reloader:
            app_config["use_reloader"] = False
        if args.ngrok_token:
            app_config["ngrok_token"] = args.ngrok_token

    def build_app_config(self, root_dir, env_filename, kwargs):
        app_config = self.app_config
        env_file_abs_path = env_filename if os.path.isabs(env_filename) else os.path.join(root_dir, env_filename)
        if os.path.isfile(env_file_abs_path):
            for key, value in dotenv_values(env_file_abs_path).items():
                key = key.lower()
                if value is not None and key in app_config:
                    try:
                        app_config[key] = value if app_config[key] is None else type(app_config[key])(value)  # type: ignore
                    except Exception as e:
                        warnings.warn(
                            f"Invalid env value in Gui.run {key} - {value}. Unable to parse value to the correct type.\n{e}"
                        )
        # Load keyword arguments
        for key, value in kwargs.items():
            key = key.lower()
            if value is not None and key in app_config:
                try:
                    app_config[key] = value if app_config[key] is None else type(app_config[key])(value)  # type: ignore
                except Exception as e:
                    warnings.warn(
                        f"Invalid keyword arguments value in Gui.run {key} - {value}. Unable to parse value to the correct type.\n{e}"
                    )
        # Load from system arguments
        self._init_argparse()
