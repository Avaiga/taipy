# Installation

The latest stable version of *taipy-common* can be installed using `pip`:
```bash
pip install taipy-common
```

## Development version

You can install the development version of *taipy-common* with `pip` and `git` directly from the Taipy repository:
```bash
pip install git+https://git@github.com/Avaiga/taipy
```

This command installs the development version of *taipy* package in the Python environment with all
its dependencies, including the *taipy-common* package.

If you need the source code for *taipy-common* on your system so you can see how things are done or
maybe participate in the improvement of the packages, you can clone the GitHub repository:

```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code, and the 'taipy-common'
source code is in the 'taipy/config' directory.

## Running the tests

To run the tests on the package, you need to install the required development packages.
We recommend using [Pipenv](https://pipenv.pypa.io/en/latest/) to create a virtual environment
and install the development packages.

```bash
pip install pipenv
pipenv install --dev
```

Then you can run *taipy-common* tests with the following command:

```bash
pipenv run pytest tests/common
```
