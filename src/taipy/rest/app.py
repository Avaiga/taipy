# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os

from flask import Flask

from . import api
from .commons.encoder import _CustomEncoder
from .extensions import apispec


def create_app(testing=False, flask_env=None, secret_key=None):
    """Application factory, used to create application"""
    app = Flask(__name__)
    app.config.update(
        ENV=os.getenv("FLASK_ENV", flask_env),
        TESTING=os.getenv("TESTING", testing),
        SECRET_KEY=os.getenv("SECRET_KEY", secret_key),
    )
    app.url_map.strict_slashes = False
    app.config["RESTFUL_JSON"] = {"cls": _CustomEncoder}

    configure_apispec(app)
    register_blueprints(app)
    with app.app_context():
        api.views.register_views()

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
