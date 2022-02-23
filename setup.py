#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "networkx",
    "numpy",
    "openpyxl",
    "pandas",
    "simple-websocket",
    "sqlalchemy",
    "toml",
    "Unidecode",
]

test_requirements = ["pytest>=3.8"]

extras_require = {
    "mssql": ["pyodbc>=4"],
    "airflow": ["taipy-airflow@git+ssh://git@github.com/Avaiga/taipy-airflow.git@develop"],
}

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
        "Programming Language :: Python :: 3.10",
    ],
    description="AI Platform for Business Applications.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="taipy-core",
    name="taipy-core",
    packages=find_packages(include=["taipy", "taipy.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/avaiga/taipy-core",
    version="0.1.0-SNAPSHOT",
    zip_safe=False,
    extras_require=extras_require,
)
