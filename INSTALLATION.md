# Installation

There are different ways to install Taipy, depending on how you plan to use it.

If your goal is to look into the code, modify and improve it, go straight
to the [source installation](#installing-for-development) section.

Taipy needs your system to have Python 3.9 or above installed.

## Installing from PyPI

The easiest way to install Taipy is from the
[Pypi software repository](https://pypi.org/project/taipy/).

Run the command:
```bash
pip install taipy
```

If you are running in a virtual environment, you will have to issue the command:
```bash
pipenv install taipy
```

These commands install the `taipy` package in the Python environment with all its
dependencies.

**Basic Usage**

```bash 
from taipy import Config
from taipy import DataSequence
from taipy import Scenario

# Create a configuration
config = Config(
    id="my_config",
    data_sequences=[
        DataSequence(
            id="my_data",
            csv_path="data.csv"
        )
    ]
)

# Create a scenario
scenario = Scenario(
    config=config,
    id="my_scenario"
)

# Run the scenario
scenario.run()
```

## Installing from GitHub

The development version of Taipy is updated daily with changes from the Taipy R&D and external
contributors whom we praise for their input.

The development version of Taipy can be installed using *pip* and *git*:

```bash
pip install git+https://git@github.com/Avaiga/taipy
```

## Installing for development

If you need the source code for Taipy on your system so you can see how things are done or maybe
participate in the improvement of the packages, you can clone the GitHub repository:

```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code.

## Running Taipy in Jupyter Notebook

```bash
import taipy as tp

# Create a configuration
config = tp.Config(...)

# Create a scenario
scenario = tp.Scenario(config)

# Run the scenario
scenario.run()
```
## Running Taipy from Command Line

```
bash
taipy run --scenario-id my_scenario
### Building the JavaScript bundles
```
## Running Taipy with Docker

```
bash
docker run -p 8080:8080 taipy/taipy:latest
```
Taipy (and Taipy GUI that it embeds) has some code dealing with the client side of the web
applications.<br/>
This code is written in [TypeScript](https://www.typescriptlang.org/), relies on
[React](https://reactjs.org/) components, and is packaged into JavaScript bundles that are sent to
browsers when they connect to all Taipy applications that have a graphical interface.

There are two main JavaScript bundles that can be built:
- Taipy GUI: All the graphical interfaces that Taipy GUI can generate are based on a set of
  generated files, including the web application and all the predefined visual elements.
- Taipy: A set of visual elements dedicated to Scenario Management.

**Prerequisites**: If you need to build the JavaScript bundle, you need to make sure that the
[Node.js](https://nodejs.org/) JavaScript runtime version 18 or above is installed on your
machine.<br/>
Note that Node.js comes with the [`npm` package manager](https://www.npmjs.com/) as part
of the standard installation.

The build process is described in the [Taipy GUI front-end](frontend/taipy-gui/README.md) and
 [Taipy front-end](frontend/taipy/README.md) README files.<br/>
 The Taipy GUI bundle must be built first, as the Taipy front-end code depends on it.

Here is the sequence of commands that can be issued to build both sets of files:

```bash
# Current directory is the repository's root directory
#
# Build the Taipy GUI bundle
cd frontend/taipy-gui
cd dom
npm i
cd ..
npm i
npm run build
#
# Build the Taipy front-end bundle
cd ../taipy # Current directory is [taipy-dir]/frontend/taipy
npm i
npm run build
```

These commands should create the directories `taipy/gui/webapp` and `taipy/gui_core/lib` in the
root directory of the taipy repository.

### Debugging the JavaScript bundles

If you plan to modify the front-end code and need to debug the TypeScript
code, you must use the following:
```bash
npm run build:dev
```

instead of the *standard* build option.

This will preserve the debugging symbols, and you will be able to navigate in the
TypeScript code from your debugger.

> **Note:** Web application location
>
> When you are developing front-end code for the Taipy GUI package, it may
> be cumbersome to have to install the package over and over when you know
> that all that has changed is the JavaScript bundle that makes the Taipy
> web app.
>
> By default, the Taipy GUI application searches for the front-end code
> in the `[taipy-gui-package-dir]/taipy/gui/webapp` directory.<br/>
> You can, however, set the environment variable `TAIPY_GUI_WEBAPP_PATH`
> to the location of your choice, and Taipy GUI will look for the web
> app in that directory.<br/>
> If you set this variable to the location where you build the web app
> repeatedly, you will no longer have to reinstall Taipy GUI before you
> try your code again.


## Running the tests

To run the tests on the package, you need to install the required development packages.
We recommend using [Pipenv](https://pipenv.pypa.io/en/latest/) to create a virtual environment
and install the development packages.

```bash
pip install pipenv
pipenv install --dev
```

Then you can run the tests with the following command:

```bash
pipenv run pytest
```
