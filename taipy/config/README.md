# Taipy Config

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
- [Taipy Config](#what-is-taipy-config)
- [Installation](#installation)
- [Contributing](#contributing)
- [Code of conduct](#code-of-conduct)
- [Directory Structure](#directory-structure)

## What is Taipy Config

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io). Taipy is split into multiple repositories including *taipy-config* to let users
install the minimum they need.

Taipy Config is a package designed to help users configure their Taipy application.

More in-depth documentation of taipy can be found [here](https://docs.taipy.io).

## Installation

Want to install *Taipy Config*? Check out our [`INSTALLATION.md`](INSTALLATION.md) file.

## Contributing

Want to help build *Taipy Config*? Check out our [`CONTRIBUTING.md`](../../CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the *Taipy Config* community? Check out our [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) file.

## Directory Structure

- `taipy/`:
  - `config/`: Configuration definition, management, and implementation. `taipy.Config` is the main entrypoint for configuring a Taipy Core application.
    - `_config_comparator/`: Internal package for comparing configurations.
    - `_serializer/`: Internal package for serializing and deserializing configurations.
    - `checker/`: Configuration checker and issue collector implementation.
    - `common/`: Shared data structures, types, and functions.
    - `exceptions/`: *taipy-config* exceptions.
    - `global_app/`: `GlobalAppConfig` implementation.
    - `stubs/`: Helper functions to create the `config.pyi` file.
    - `CODE_OF_CONDUCT.md`: Code of conduct for members and contributors of *taipy-config*.
    - `INSTALLATION.md`: Instructions to install *taipy-config*.
    - `LICENSE`: The Apache 2.0 License.
    - `README.md`: Current file.
    - `setup.py`: The setup script managing building, distributing, and installing *taipy-config*.
  - `logger/`: Taipy logger implementation.
- `tests/`:
  - `config/`: Tests for the *taipy-config* package.
