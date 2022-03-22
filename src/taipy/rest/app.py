import os

from flask import Flask

from . import api
from .config import TAIPY_SETUP_FILE
from .extensions import apispec, db, migrate
from importlib.util import find_spec


def create_app(testing=False):
    """Application factory, used to create application"""
    app = Flask("src.taipy.rest")
    app.config.from_object("src.taipy.rest.config")

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app)
    configure_apispec(app)
    register_blueprints(app)

    if gui_installed():
        from taipy.gui import Gui, Markdown
        abs_folder, _ = TAIPY_SETUP_FILE.rsplit("/", 1)
        gui = Gui(flask=app, pages={"demo": Markdown(os.path.join(abs_folder, "demo.md"))})
        gui.run(run_server=False)

    return app


def gui_installed() -> bool:
    """Check if taipy.gui is installed"""
    return find_spec("taipy.gui") is not None


def configure_extensions(app):
    """Configure flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)


def configure_apispec(app):
    """Configure APISpec for swagger support"""
    apispec.init_app(app)

    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def register_blueprints(app):
    """Register all blueprints for application"""
    app.register_blueprint(api.views.blueprint)
