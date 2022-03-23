"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from passlib.context import CryptContext

from .commons.apispec import APISpecExt

ma = Marshmallow()
migrate = Migrate()
apispec = APISpecExt()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
