# Default config loaded by app.py

default_config = {
    "app_config": {"port": 5000, "dark_mode": True, "debug": True, "host": "127.0.0.1", "timezone": "client"},
    "style_config": {
        "button": "px-2 py-1 rounded border border-gray-300 bg-gray-200 hover:bg-gray-300 hover:bg-gray-300 dark:bg-gray-800 dark:border-gray-900 dark:text-white dark:hover:bg-gray-900 cursor-pointer",  # noqa
        "field": "text-lime-600 dark:text-lime-400 font-semibold",
        "input": "px-2 py-1 rounded border border-gray-300 dark:border-gray-800 dark:bg-gray-700 dark:text-white",  # noqa
        "slider": "appearance-none rounded-lg overflow-hidden dark:bg-gray-600 ring-lime-400",  # noqa
        "date_selector": "",
        "table": "",
    },
}
