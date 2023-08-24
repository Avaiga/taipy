# Taipy Core

[![Python](https://img.shields.io/pypi/pyversions/taipy-core)](https://pypi.org/project/taipy-core)
[![PyPI](https://img.shields.io/pypi/v/taipy-core.svg?label=pip&logo=PyPI&logoColor=white)](https://pypi.org/project/taipy-core)

## License

Copyright 2023 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Usage

- [Taipy Core](#taipy-core)
- [License](#license)
- [Usage](#usage)
- [What is Taipy Core](#what-is-taipy-core)
- [Installation](#installation)
- [Contributing](#contributing)
- [Code of conduct](#code-of-conduct)
- [Directory Structure](#directory-structure)

## What is Taipy Core

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io). Taipy is split into multiple repositories including _taipy-core_ to let users
install the minimum they need.

[Taipy Core](https://github.com/Avaiga/taipy-core) mostly includes business-oriented features. It helps users
create and manage business applications and improve analyses capability through time, conditions and hypothesis.

A more in depth documentation of taipy can be found [here](https://docs.taipy.io).

## Installation

Want to install _Taipy Core_? Check out our [`INSTALLATION.md`](INSTALLATION.md) file.

## Contributing

Want to help build _Taipy Core_? Check out our [`CONTRIBUTING.md`](CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the _Taipy Core_ community? Check out our [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) file.

## Directory Structure

- `src/`:
  - `taipy/core/`:
    - `_manager`: Internal package for entity manager.
    - `_repository`: Internal package for data storage.
    - `_orchestrator`: Internal package for task orchestrating and execution.
    - `_version`: Internal package for managing Taipy Core application version.
    - `common`: Shared data structures, types, and functions.
    - `config`: Configuration definition, management and implementation. `config.config.Config` is the main
      entrypoint for configuring a Taipy Core application.
    - `cycle`: Work cycle definition, management and implementation.
    - `data`: Data Node definition, management and implementation.
    - `exceptions`: _taipy-core_ exceptions.
    - `job`: Job definition, management and implementation.
    - `sequence`: Sequence definition, management and implementation.
    - `scenario`: Scenario definition, management and implementation.
    - `task`: Task definition, management and implementation.
    - `taipy`: Main entrypoint for _taipy-core_ runtime features.
- `tests`: Unit tests following the `taipy/core/` structure.
- `CODE_OF_CONDUCT.md`: Code of conduct for members and contributors of _taipy-core_.
- `CONTRIBUTING.md`: Instructions to contribute to _taipy-core_.
- `INSTALLATION.md`: Instructions to install _taipy-core_.
- `LICENSE`: The Apache 2.0 License.
- `Pipfile`: File used by the Pipenv virtual environment to manage project dependencies.
- `README.md`: Current file.
- `contributors.txt`: The list of contributors.
- `setup.py`: The setup script managing building, distributing, and installing _taipy-core_.
- `tox.ini`: Contains test scenarios to be run.
