# Taipy Core

## License

Copyright 2021-2024 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions
and limitations under the License.

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
[website](https://www.taipy.io). Taipy is split into multiple packages including
*taipy-core* to let users install the minimum they need.

Taipy Core mostly includes business-oriented
features. It helps users create and manage business applications and improve analyses
capability through time, conditions and hypothesis.

A more in depth documentation of taipy can be found [here](https://docs.taipy.io).

## Installation

Want to install *Taipy Core*? Check out our [`INSTALLATION.md`](INSTALLATION.md) file.

## Contributing

Want to help build *Taipy Core*? Check out our [`CONTRIBUTING.md`](../../CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the *Taipy Core* community? Check out our
[`CODE_OF_CONDUCT.md`](../../CODE_OF_CONDUCT.md) file.

## Directory Structure

- `taipy/`:
  - `core/`:
    - `_entity/`: Internal package for abstract entity definition and entity's properties management.
    - `_manager/`: Internal package for entity manager.
    - `_orchestrator/`: Internal package for task orchestrating and execution.
    - `_repository/`: Internal package for data storage.
    - `_version/`: Internal package for managing Taipy Core application version.
    - `common/`: Shared data structures, types, and functions.
    - `config/`: Configuration definition, management and implementation.
    - `cycle/`: Work cycle definition, management and implementation.
    - `data/`: Data Node definition, management and implementation.
    - `exceptions/`: *taipy-core* exceptions.
    - `job/`: Job definition, management and implementation.
    - `notification/`: Notification management system implementation.
    - `scenario/`: Scenario definition, management and implementation.
    - `sequence/`: Sequence definition, management and implementation.
    - `submission/`: Submission definition, management and implementation.
    - `task/`: Task definition, management and implementation.
    - `taipy.py`: Main entrypoint for *taipy-core* runtime features.
    - `INSTALLATION.md`: Instructions to install *taipy-core*.
    - `LICENSE`: The Apache 2.0 License.
    - `README.md`: Current file.
    - `setup.py`: The setup script managing building, distributing, and installing *taipy-core*.
- `tests/`:
  - `core/`: Unit tests following the `taipy/core/` structure.
