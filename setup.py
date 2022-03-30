#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "taipy-gui@git+ssh://git@github.com/Avaiga/taipy-gui.git@develop",
    "taipy-core@git+ssh://git@github.com/Avaiga/taipy-core.git@develop",
    "taipy-rest@file:///home/vuille_f/Documents/avaiga/taipy-rest",
]

extras_require = {
    "ngrok": ["pyngrok>=5"],
    "image": ["python-magic;platform_system!='Windows'", "python-magic-bin;platform_system=='Windows'"],
    "rdp": ["rdp>=0.8"],
    "arrow": ["pyarrow>=7.0"],
    "mssql": ["pyodbc>=4"],
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
    keywords="taipy",
    name="taipy",
    packages=find_packages(include=['taipy']),
    url="https://github.com/avaiga/taipy",
    version="1.0.0.dev",
    zip_safe=False,
    extras_require=extras_require,
)
