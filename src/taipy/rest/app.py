import os
from flask import Flask

from . import api
from .extensions import apispec


def create_app(testing=False, flask_env=None, secret_key=None):
    """Application factory, used to create application"""
    app = Flask(__name__)
    app.config.update(
        ENV=os.getenv("FLASK_ENV", flask_env),
        TESTING=os.getenv("TESTING", testing),
        SECRET_KEY=os.getenv("SECRET_KEY", secret_key)
    )

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
