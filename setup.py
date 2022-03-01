#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup, find_namespace_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "taipy-gui@git+ssh://git@github.com/Avaiga/taipy-gui.git@develop",
    "taipy-core@git+ssh://git@github.com/Avaiga/taipy-core.git@develop",
]

extras_require = {
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
    keywords="taipy",
    name="taipy",
    packages=find_packages(include=['taipy']),
    url="https://github.com/avaiga/taipy",
    version="0.1.2",
    zip_safe=False,
    extras_require=extras_require,
)

