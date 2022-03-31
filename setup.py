#!/usr/bin/env python

"""The setup script."""

import os
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

with open("README.md") as readme_file:
    readme = readme_file.read()


requirements = [
    "flask",
    "flask-cors",
    "flask-socketio",
    "markdown",
    "numpy",
    "pandas",
    "python-dotenv",
    "pytz",
    "simple-websocket",
    "tzlocal",
    "backports.zoneinfo;python_version<'3.9'",
]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "ngrok": ["pyngrok>=5"],
    "image": ["python-magic;platform_system!='Windows'", "python-magic-bin;platform_system=='Windows'"],
    "rdp": ["rdp>=0.8"],
    "arrow": ["pyarrow>=7.0"],
}


def _build_webapp():
    already_exists = Path(f"./taipy/gui/webapp/index.html").exists()
    if not already_exists:
        os.system("cd gui && npm ci && npm run build")


class NPMInstall(build_py):
    def run(self):
        _build_webapp()
        build_py.run(self)


setup(
    author="Avaiga",
    author_email="taipy.dev@avaiga.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="AI Platform for Business Applications.",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords="taipy-gui",
    name="taipy-gui",
    packages=find_packages(include=["taipy", "taipy.gui", "taipy.gui.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-gui",
    version="1.0.0.dev",
    zip_safe=False,
    extras_require=extras_require,
    cmdclass={"build_py": NPMInstall},
)
