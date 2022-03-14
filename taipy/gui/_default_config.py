from .config import Config

# Default config loaded by app.py
default_config: Config = {
    "port": 5000,
    "dark_mode": True,
    "debug": True,
    "host": "127.0.0.1",
    "use_reloader": True,
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
    "notification_duration": 3000,
    "single_client": False,
    "ngrok_token": "",
    "upload_folder": None,
    "flask_log": False,
    "margin": "1em",
}
