from setuptools import setup

__version__ = "1.0.0.dev"

setup(
    name="taipy_rest",
    version=__version__,
    packages=["taipy.rest"],
    package_dir={'taipy': 'src/taipy'},
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-restful",
        "flask-migrate",
        "flask-jwt-extended",
        "flask-marshmallow",
        "marshmallow-sqlalchemy",
        "python-dotenv",
        "passlib",
        "apispec[yaml]",
        "apispec-webframeworks",
        "taipy-core@git+ssh://git@github.com/Avaiga/taipy-core.git@develop"
    ],
)
