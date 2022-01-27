import importlib

from flask import Flask

from taipy_rest import api
from taipy_rest.extensions import apispec, db, migrate
from taipy.gui import Gui, Markdown
from taipy_rest.config import TAIPY_SETUP_FILE
import os


# def _routes(app):
#     routes = []
#     for route in app.url_map.iter_rules():
#         routes.append('%s' % route)
#     return routes


def create_app(testing=False):
    """Application factory, used to create application"""
    app = Flask("taipy_rest")
    app.config.from_object("taipy_rest.config")

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app)
    configure_apispec(app)
    register_blueprints(app)
    # spec = importlib.util.spec_from_file_location("taipy_setup", TAIPY_SETUP_FILE)
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)

    abs_folder, _ = TAIPY_SETUP_FILE.rsplit("/", 1)
    gui = Gui(flask=app, pages={"demo": Markdown(os.path.join(abs_folder, "demo.md"))})
    gui.run(run_server=False)
    return app


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
