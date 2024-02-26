# Installation

The latest stable version of *taipy-config* can be installed using `pip`:
```bash
pip install taipy-config
```

## Development version

You can install the development version of *taipy-config* with `pip` and `git` directly from the Taipy repository:
```bash
pip install git+https://git@github.com/Avaiga/taipy
```

This command installs the development version of _taipy_ package in the Python environment with all
its dependencies, including the _taipy-config_ package.

If you need the source code for _taipy-config_ on your system so you can see how things are done or
maybe participate in the improvement of the packages, you can clone the GitHub repository:

```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code, and the 'taipy-config'
source code is in the 'taipy/config' directory.

## Running the tests

To run the tests on the package, you need to install the required development packages.
We recommend using [Pipenv](https://pipenv.pypa.io/en/latest/) to create a virtual environment
and install the development packages.

```bash
pip install pipenv
pipenv install --dev
```

Then you can run *taipy-config* tests with the following command:

```bash
pipenv run pytest tests/config
```
