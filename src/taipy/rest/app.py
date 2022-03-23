import os

from flask import Flask

from . import api
from .extensions import apispec, migrate


def create_app(testing=False):
    """Application factory, used to create application"""
    app = Flask("src.taipy.rest")
    app.config.from_object("src.taipy.rest.config")

    if testing is True:
        app.config["TESTING"] = True

    configure_apispec(app)
    register_blueprints(app)

    return app


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
