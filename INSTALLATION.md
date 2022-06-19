# Installation

The latest stable version of _taipy-toolkit_ is available through _pip_:
```
pip install taipy-toolkit
```

## Development version

You can install the development version of _taipy-toolkit_ with _pip_ and _git_:
```
pip install git+https://git@github.com/Avaiga/taipy-toolkit
```

## Work with the _taipy-toolkit_ code
```
git clone https://github.com/Avaiga/taipy-toolkit.git
cd taipy-toolkit
pip install .
```

If you want to run tests, please install `Pipenv`:
```
pip install pipenv
git clone https://github.com/Avaiga/taipy-toolkit.git
cd taipy-toolkit
pipenv install --dev
pipenv run pytest
```
