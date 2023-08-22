# Taipy-REST
[![Python](https://img.shields.io/pypi/pyversions/taipy-rest)](https://pypi.org/project/taipy-rest)
[![PyPI](https://img.shields.io/pypi/v/taipy-rest.svg?label=pip&logo=PyPI&logoColor=white)](https://pypi.org/project/taipy-rest)


## License
Copyright 2023 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Usage
  -  [Taipy-REST](#taipy-rest)
  - [License](#license)
  - [Usage](#usage)
  - [What is Taipy REST](#what-is-taipy-rest)
  - [Installation](#installation)
  - [Contributing](#contributing)
  - [Code of conduct](#code-of-conduct)
  - [Directory Structure](#directory-structure)


## What is Taipy REST

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io). Taipy is split into multiple repositories including _taipy-core_ and _taipy-rest_
to let users install the minimum they need.

[Taipy Core](https://github.com/Avaiga/taipy-core) mostly includes business-oriented features. It helps users
create and manage business applications and improve analyses capability through time, conditions and hypothesis.

[Taipy REST](https://github.com/Avaiga/taipy-rest) is a set of APIs built on top of the _taipy-core_ library
developed by Avaiga. This project is meant to be used as a complement for **taipy** and its goal is to enable
automation through rest APIs of processes built on taipy.

The project comes with rest APIs that provide interaction with all of taipy modules:
 - DataNodes
 - Tasks
 - Jobs
 - Sequences
 - Scenarios
 - Cycles

A more in depth documentation of taipy can be found [here](https://docs.taipy.io).

## Installation

Want to install and try _Taipy REST_? Check out our [`INSTALLATION.md`](INSTALLATION.md) file.

## Contributing

Want to help build _Taipy REST_? Check out our [`CONTRIBUTING.md`](CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the _Taipy REST_ community? Check out our [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) file.

## Directory Structure

- `src/taipy/rest`: Main source code folder.
    - `api`: Endpoints and schema definitions.
      - `resources`: Implementation of all endpoints related to taipy.
      - `schemas`: Schemas related to taipy objects. Used for marshalling and unmarshalling data.
      - `views`: Mapping of resources to urls
    - `commons`: Common files shared throughout the application
      - `templates`: Swagger and redoc templates for generating the documentation
    - `app.py`: Flask app configuration and creation
    - `extensions.py`: Singletons used on the application factory
    - `rest.py`: Main python entrypoint for running _taipy-rest_ application.
- `tests`: Unit tests.
- `CODE_OF_CONDUCT.md`: Code of conduct for members and contributors of _taipy-rest_.
- `CONTRIBUTING.md`: Instructions to contribute to _taipy-rest_.
- `INSTALLATION.md`: Instructions to install _taipy-rest_.
- `LICENSE`: The Apache 2.0 License.
- `Pipfile`: File used by the Pipenv virtual environment to manage project dependencies.
- `README.md`: Current file.
- `contributors.txt`: The list of contributors
- `setup.py`: The setup script managing building, distributing, and installing _taipy-rest_.
- `tox.ini`: Contains test scenarios to be run.
