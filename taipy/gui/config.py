import tzlocal
import pytz


class GuiConfig(object):
    def __init__(self):
        self.pages = []
        self.routes = []
        self.app_config = {}
        self.style_config = {}

    def load_config(self, app_config={}, style_config={}) -> None:
        self.app_config.update(app_config)
        self.style_config.update(style_config)
        # Run get_timezone to veriy user predefined IANA timezone if available
        self.get_timezone()

    def get_timezone(self) -> str:
        if "timezone" not in self.app_config or self.app_config["timezone"] == "client":
            return "client"
        if self.app_config["timezone"] == "server":
            # return python tzlocal IANA Timezone
            return str(tzlocal.get_localzone())
        # Verify user defined IANA Timezone is valid
        if self.app_config["timezone"] not in pytz.all_timezones_set:
            raise Exception("User defined IANA timezone configuration is not valid!")
        # return user defined IANA Timezone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
        return self.app_config["timezone"]
