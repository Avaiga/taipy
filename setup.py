#!/usr/bin/env python

"""The setup script."""

from typing import List

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("docs/history.md") as history_file:
    history = history_file.read()

requirements: List[str] = [
    "flask",
    "flask-cors",
    "flask-socketio",
    "markdown",
    "networkx",
    "numpy",
    "pandas",
    "pyodbc",
    "pytz",
    "sqlalchemy",
    "simple-websocket",
    "toml",
    "tzlocal",
    "Unidecode",
]

test_requirements = [
    "pytest>=3.8",
    "python-magic",
    "python-magic-bin"
]

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
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="taipy",
    name="taipy",
    packages=find_packages(include=["taipy", "taipy.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy",
    version="0.1.2",
    zip_safe=False,
    extras_require={
        "ngrok": ["pyngrok>=5"],
        "magic": ["python-magic", "python-magic-bin"],
    },
)
