import typing as t

import pytz
import tzlocal

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
        self.style_config: t.Dict = {}

    def load_config(self, app_config={}, style_config={}) -> None:
        self.app_config.update(app_config)
        self.style_config.update(style_config)
        # Run get_time_zone to verify user predefined IANA time_zone if available
        self.get_time_zone()

    def _get_app_config(self, name: AppConfigOption, defaultValue: t.Any) -> t.Any:
        if name in self.app_config and self.app_config[name] is not None:
            return self.app_config[name]
        return defaultValue

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
