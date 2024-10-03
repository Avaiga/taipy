# Taipy Common

## License
Copyright 2021-2024 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Usage
- [License](#license)
- [Usage](#usage)
- [Taipy Common](#what-is-taipy-common)
- [Installation](#installation)
- [Contributing](#contributing)
- [Code of conduct](#code-of-conduct)
- [Directory Structure](#directory-structure)

## What is Taipy Common

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io). Taipy is split into multiple packages including *taipy-common* to let users
install the minimum they need.

Taipy Common is a package designed to have the code that serves as basis for the other Taipy packages,
including classes and methods to enable logging, cli and users to configure their Taipy application.

More in-depth documentation of taipy can be found [here](https://docs.taipy.io).

## Installation

Want to install *Taipy Common*? Check out our [`INSTALLATION.md`](INSTALLATION.md) file.

## Contributing

Want to help build *Taipy Common*? Check out our [`CONTRIBUTING.md`](../../CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the *Taipy Common* community? Check out our [`CODE_OF_CONDUCT.md`](../../CODE_OF_CONDUCT.md) file.

## Directory Structure

- `taipy/`:
  - `common/`: Common data structures, types, and functions.
    - `config/`: Configuration definition, management, and implementation. `taipy.Config` is the main entrypoint for configuring a Taipy Core application.
      - `_config_comparator/`: Internal package for comparing configurations.
      - `_serializer/`: Internal package for serializing and deserializing configurations.
      - `checker/`: Configuration checker and issue collector implementation.
      - `common/`: Shared data structures, types, and functions.
      - `exceptions/`: *taipy-common* exceptions.
      - `global_app/`: `GlobalAppConfig` implementation.
      - `stubs/`: Helper functions to create the `config.pyi` file.
      - `INSTALLATION.md`: Instructions to install *taipy-common*.
      - `LICENSE`: The Apache 2.0 License.
      - `README.md`: Current file.
      - `setup.py`: The setup script managing building, distributing, and installing *taipy-common*.
    - `logger/`: Taipy logger implementation.
- `tests/`:
  - `common/`: Tests for the *taipy-common* package.
