# Installation

The latest stable version of _taipy-gui_ is available through _pip_:
```
pip install taipy-gui
```

## Development version

You can install the development version of _taipy_ with _pip_ and _git_:
```
pip install git+https://git@github.com/Avaiga/taipy-gui
```

## Work with the _taipy-gui_ code
```
git clone https://github.com/Avaiga/taipy-gui.git
cd taipy-gui
pip install .
```

If you want to run tests, please install `Pipenv`:
```
pip install pipenv
git clone https://github.com/Avaiga/taipy-gui.git
cd taipy-gui
pipenv install --dev
pipenv run pytest
```