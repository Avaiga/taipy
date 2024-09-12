# Taipy templates

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
  - [Taipy](#taipy)
  - [License](#license)
  - [Usage](#usage)
  - [What is Taipy templates](#what-is-taipy-templates)
  - [Contributing](#contributing)
  - [Code of conduct](#code-of-conduct)
  - [Directory Structure](#directory-structure)

## What is Taipy templates

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io).

Taipy templates is a repository that contains application templates created and
maintained by Taipy. It helps users getting started with a simple and ready-to-go application.

A more in depth documentation of taipy can be found [here](https://docs.taipy.io).

To create a Taipy application using this template, first you need to install Taipy (> 2.2).
Then from a terminal, run the following command.
```bash
taipy create
```
or
```bash
taipy create --application "default"
```

After providing necessary information, your new application is created in the current
working directory.

## Contributing

Want to help build *Taipy*? Check out our [`CONTRIBUTING.md`](../../CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the *Taipy* community? Check out our
[`CODE_OF_CONDUCT.md`](../../CODE_OF_CONDUCT.md) file.

## Directory Structure

- `taipy/`:
  - `templates/`: Contains templates, each in a dedicated sub-folder with the following structure:
    - `<template-name>/`: Internal package for Taipy data backup mechanism.
      - `{{cookiecutter.__root_folder}}/`: The root folder of the application created using this template.
      - `hooks/`: Contains hooks to be executed before and after the application is created.
      - `cookiecutter.json`: The configuration file for the template.
    - `LICENSE`: The Apache 2.0 License.
    - `README.md`: Current file.
    - `setup.py`: The setup script managing building, distributing, and installing *taipy-templates*.
- `tests/`:
  - `templates/`: Unit tests following the `taipy/templates/` structure.
