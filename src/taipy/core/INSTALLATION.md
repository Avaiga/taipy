# Installation

The latest stable version of _taipy-core_ is available through _pip_:
```
pip install taipy-core
```

## Development version

You can install the development version of _taipy_ with _pip_ and _git_:
```
pip install git+https://git@github.com/Avaiga/taipy-core
```

## Work with the _taipy-core_ code
```
git clone https://github.com/Avaiga/taipy-core.git
cd taipy-core
pip install .
```

If you want to run tests, please install `Pipenv`:
```
pip install pipenv
git clone https://github.com/Avaiga/taipy-core.git
cd taipy-core
pipenv install --dev
pipenv run pytest
```
