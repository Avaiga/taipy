# Installation

The latest stable version of _taipy-core_ is available through _pip_:
```bash
pip install taipy-core
```

## Development version

You can install the development version of _taipy-core_ with _pip_ and _git_ via the taipy repository:
```bash
$ pip install git+https://git@github.com/Avaiga/taipy
```

This command installs the development version of _taipy_ package in the Python environment with all
its dependencies, including the _taipy-core_ package.

If you need the source code for _taipy-core_ on your system so you can see how things are done or
maybe participate in the improvement of the packages, you can clone the GitHub repository:

```bash
$ git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code, and the 'taipy-core'
source code is in the 'taipy/core' directory.

## Running the tests

To run the tests on the package, you need to install the required development packages.
We recommend using [Pipenv](https://pipenv.pypa.io/en/latest/) to create a virtual environment
and install the development packages.

```bash
$ pip install pipenv
$ pipenv install --dev
```

Then you can run _taipy-core_ tests with the following command:

```bash
$ pipenv run pytest tests/core
```
