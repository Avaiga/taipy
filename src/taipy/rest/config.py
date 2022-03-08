"""Default configuration

Use env var to override
"""
import os
import pathlib

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

TAIPY_SETUP_FILE = os.getenv(
    "TAIPY_SETUP_FILE",
    os.path.join(pathlib.Path(__file__).parent.absolute(), "setup/config.py"),
)
