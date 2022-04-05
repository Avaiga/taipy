# Overview

## What is Taipy

Taipy is a Python framework for creating Business Applications.
More information on our website: `https://www.taipy.io`.

## What is _taipy-core_

Taipy is split into multiple repositories so that a minimal installation can be performed.

_taipy-core_ mostly includes business-oriented features. It helps users
create and manage business applications and improve analyses capability through time,
conditions and hypothesis.

## Installation

### With Pip

You can install the development version of _taipy-core_ with `pip`.
```
pip install git+ssh://git@github.com/Avaiga/taipy-core
```

### By cloning
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


## Directory Structure

The files needed to build _taipy-core_ are located in sub-directories that
store files as follows:

-   `taipy/core`:
    - `_repository`: Internal layer for data saving and loading.
    - `_scheduler`: Internal layer for task execution.
    - `common`: Shared data structures and types.
    - `config`: Configuration and checker allowing definition of application.
    - `cycle`: Work cycle definition, management and implementation.
    - `data`: Data Node definition, management and implementation.
    - `exceptions`: _taipy-core_ exceptions.
    - `job`: Job definition, management and implementation.
    - `pipeline`: Pipeline definition, management and implementation.
    - `scenario`: Scenario definition, management and implementation.
    - `tasks`: Task definition, management and implementation.
    - `taipy`: Official interface of _taipy-core_.
-   `tests`: Tests following the `taipy/core` structure.
-   `tox.ini`: Contains test scenarios to be run.
-   `.github`: Github configuration with Actions configurations for running tests in our CI.
