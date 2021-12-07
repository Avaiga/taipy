from .config import AppConfig, StyleConfig

# Default config loaded by app.py
app_config_default: AppConfig = {
    "port": 5000,
    "dark_mode": True,
    "debug": True,
    "host": "127.0.0.1",
    "time_zone": "client",
    "propagate": True,
    "client_url": "http://127.0.0.1:5000",
    "favicon": None,
    "title": None,
    "theme": None,
    "theme[light]": None,
    "theme[dark]": None,
    "use_arrow": False,
    "browser_notification": True,
}

style_config_default: StyleConfig = {
    "button": "",
    "field": "",
    "input": "",
    "slider": "",
    "date_selector": "",
    "table": "",
    "selector": "",
    "tree": "",
    "dialog": "",
    "chart": "",
    "status": "",
    "toggle": "",
    "navbar": "",
    "layout": "",
    "part": "",
    "expandable": "",
}
