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

## What is Taipy Core

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io). Taipy is split into multiple repositories including *taipy-core*
to let users install the minimum they need.

Taipy Core mostly includes business-oriented features. It helps users create and manage business
applications and improve analyses capability through time, conditions and hypothesis.

## Installation

The latest stable version of *taipy-core* is available through *pip*:
```bash
pip install taipy-core
```

You can install the development version of *taipy-core* with *pip* and *git* via the taipy repository:
```bash
pip install git+https://git@github.com/Avaiga/taipy
```

This command installs the development version of *taipy* package in the Python environment with all
its dependencies, including the *taipy-core* package.

If you need the source code for *taipy-core* on your system so you can see how things are done or
maybe participate in the improvement of the packages, you can clone the GitHub repository:

```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code, and the 'taipy-core'
source code is in the 'taipy/core' directory.

## Running the tests

To run the tests on the package, you need to install the required development packages.
We recommend using [Pipenv](https://pipenv.pypa.io/en/latest/) to create a virtual environment
and install the development packages.

```bash
pip install pipenv
pipenv install --dev
```

Then you can run *taipy-core* tests with the following command:

```bash
pipenv run pytest tests/core
```

## Contributing

Want to help build *Taipy Core*? Check out our
 [Contributing Guide](https://docs.taipy.io/en/latest/contributing/contributing/).

## Code of conduct

Taipy is an open source project developed by the Taipy development team and a community of
[contributors](https://docs.taipy.io/en/latest/contributing/contributors/). Please check out the
[Taipy Code of Conduct](https://docs.taipy.io/en/latest/contributing/code_of_conduct/) for guidance
on how to interact with others in a way that makes our community thrive.
