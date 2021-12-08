import typing as t

import pytz
import tzlocal
import warnings

from .page import Page, Partial

AppConfigOption = t.Literal[
    "port",
    "dark_mode",
    "debug",
    "host",
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
]

AppConfig = t.TypedDict(
    "AppConfig",
    {
        "port": int,
        "dark_mode": bool,
        "debug": bool,
        "host": str,
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
    },
    total=False,
)

StyleConfig = t.TypedDict(
    "StyleConfig",
    {
        "button": str,
        "field": str,
        "input": str,
        "slider": str,
        "date_selector": str,
        "table": str,
        "selector": str,
        "tree": str,
        "dialog": str,
        "chart": str,
        "status": str,
        "toggle": str,
        "navbar": str,
        "layout": str,
        "part": str,
        "expandable": str,
    },
    total=False,
)


class GuiConfig(object):
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
