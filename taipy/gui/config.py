import os
import re
import sys
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

    def load_app_config_runtime(self, root_dir, env_filename, kwargs):  # noqa: C901
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
        pointer = 1
        while pointer < (argv_len := len(argv := sys.argv)):
            arg = argv[pointer]
            if arg in ["-p", "--port"]:
                if pointer == argv_len - 1:
                    warnings.warn("Missing port value for --port option")
                    break
                arg_value = argv[pointer + 1]
                if not GuiConfig.__RE_PORT_NUMBER.match(arg_value):
                    warnings.warn("Port value for --port option is not valid")
                    pointer += 1
                    continue
                app_config["port"] = int(arg_value)
                pointer += 1
            if arg in ["-h", "--host"]:
                if pointer == argv_len - 1 or "-" in argv[pointer + 1]:
                    warnings.warn("Missing host value for --host option")
                    pointer += 1
                    continue
                app_config["host"] = argv[pointer + 1]
                pointer += 1
            if arg in ["-c", "--client-url"]:
                if pointer == argv_len - 1 or "-" in argv[pointer + 1]:
                    warnings.warn("Missing url value for --client-url option")
                    pointer += 1
                    continue
                app_config["client_url"] = argv[pointer + 1]
                pointer += 1
            if arg in ["--debug"]:
                app_config["debug"] = True
            if arg in ["--no-debug"]:
                app_config["debug"] = False
            if arg in ["--use-reloader"]:
                app_config["use_reloader"] = True
            if arg in ["--no-reloader"]:
                app_config["use_reloader"] = False
            pointer += 1
