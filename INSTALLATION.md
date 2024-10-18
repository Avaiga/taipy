Welcome to the installation section of the Taipy web application builder! This section will
guide you through the seamless and straightforward process of setting up and deploying your
own powerful web applications.

- If you just want to use the package as is, please refer to the
[Installing Taipy library](#installing-taipy-library) section.<br/>

- If you aim to modify the code or contribute to its development, refer to the
[Installing development environment](#installing-development-environment) section.


# Installing Taipy library

## Prerequisite

Before installing Taipy, ensure you have Python (**version 3.9 or later**) and
[pip](https://pip.pypa.io) installed on your system. If you don't have pip installed, you can
follow these steps to install it:

1. **[Python Installation Guide](http://docs.python-guide.org/en/latest/starting/installation/)**:
    Follow the installation guide to set up Python on your system.
    After the installation, you can open the Command Prompt and type `python --version` to check
    the installed Python version.

2. **[Installing pip](https://pip.pypa.io/en/latest/installation/)**: Pip is included by default
    if you use Python 3.4 or later. Otherwise, you can follow the official
    installation page of pip to install it. To verify the installation, type `pip --version` or
    `pip3 --version`.

Alternatively, if you are using a Conda environment, you can install pip using the following
command:
```console
conda install pip
```

## The latest stable release from Pypi

### Pip
The preferred method to install Taipy is by using **pip**. After downloading Taipy package
from **[PyPI repository](https://pypi.org/project/taipy/)** the following commands install
it in the Python environment with all its dependencies. Open your terminal or command prompt
and run the following command:
```console
pip install taipy
```

### Pipenv
If you are using a virtual environment with **[Pipenv](https://pipenv.pypa.io/en/latest/)**,
use the following command:
```console
pipenv install taipy
```

### Venv
Alternatively, you can use `venv` to create a virtual environment. Please run the following
commands replacing `<myenv>` (twice) with your desired environment name:
```console
python -m venv <myenv>
source myenv/bin/activate  # On Windows use `<myenv>\Scripts\activate`
pip install taipy
```

### Conda
If you prefer to work within a [Conda](https://docs.conda.io/projects/conda/en/latest/index.html)
environment, you can install Taipy using the following commands replacing `<myenv>` with your
desired environment name:
```console
conda create -n <myenv>
conda activate <myenv>
pip install taipy
```

## A specific version from PyPI

### Pip
To install a specific version of Taipy, use the following command replacing `<version>` with a
specific version number of Taipy among the
**[list of all released Taipy versions](https://pypi.org/project/taipy/#history)**:
```console
pip install taipy==<version>
```

### Pipenv
If you are using a virtual environment with **[Pipenv](https://pipenv.pypa.io/en/latest/)**,
use the following command:
```console
pipenv install taipy==<version>
```

### Venv
Alternatively, you can use `venv` to create a virtual environment:
```console
python -m venv myenv
source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
pip install taipy==<version>
```

### Conda
If you prefer to work within a [Conda](https://docs.conda.io/projects/conda/en/latest/index.html)
environment, you can install Taipy using the following commands replacing `<myenv>` with your
desired environment name:
```console
conda create -n <myenv>
conda activate <myenv>
pip install taipy==<version>
```

## A development version from GitHub

### Pip
The development version of Taipy is hosted on
**[GitHub repository](https://git@github.com/Avaiga/taipy)** using the `develop` branch. This
branch is updated daily with changes from the Taipy R&D team and external contributors whom we
praise for their input.

The development version of Taipy can be installed using **pip**. After downloading Taipy source
code from the **[GitHub repository](https://git@github.com/Avaiga/taipy) the following commands
build the package, and install it in the Python environment with all its dependencies.

Open your terminal or command prompt and run the following command:

```bash
pip install git+https://git@github.com/Avaiga/taipy
```

### Pipenv
If you are using a virtual environment with **[Pipenv](https://pipenv.pypa.io/en/latest/)**,
use the following command:
```console
pipenv install git+https://git@github.com/Avaiga/taipy
```

### Venv
Alternatively, you can use `venv` to create a virtual environment:
```console
python -m venv myenv
source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
pip install git+https://git@github.com/Avaiga/taipy
```

### Conda
If you prefer to work within a [Conda](https://docs.conda.io/projects/conda/en/latest/index.html)
environment, you can install Taipy using the following commands replacing `<myenv>` with your
desired environment name:
```console
conda create -n <myenv>
conda activate <myenv>
pip install git+https://git@github.com/Avaiga/taipy
```

# Installing Taipy with Colab

Google Colab is a popular and free Jupyter notebook environment that requires no setup
and runs entirely in the cloud. To install Taipy in Google Colab, follow these simple
steps:

1. **Open a new Colab notebook**: Visit [Google Colab](https://colab.research.google.com)
    and start a new notebook.

2. **Run the installation command**: In a new cell, enter the following command and run
    the cell to install the latest stable release of Taipy in your Colab environment:

    ```python
    !pip install --ignore-installed taipy
    ```

3. **Start building your app**: Follow this
    [tutorial](https://docs.taipy.io/en/latest/tutorials/articles/colab_with_ngrok/) to build
    and run your Taipy web application directly within the Colab notebook.

!!! tip
    Remember that Google Colab environments are ephemeral. If you disconnect or restart
    your Colab session, you will need to reinstall Taipy.

# Installing the development kit

If you need the source code for Taipy on your system to see how things are done or maybe
contribute to the improvement of the packages, you can set your environment up by following
the steps below.

## Prerequisites
Before installing the Taipy development kit, ensure you have
[Python](http://docs.python-guide.org/en/latest/starting/installation/) (**version 3.9 or later**),
[pip](https://pip.pypa.io/en/latest/installation/), and
[git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed on your system.

??? note "On Mac OS M1 pro"

    If you are using a Mac OS M1 pro, you may need to install the `libmagic` library before.
    Please run the commands below:
    ```bash
    brew install libmagic
    pip install python-libmagic
    ```

## Cloning the repository

First, clone the Taipy repository from GitHub using the following command:

```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code.

## Building the JavaScript bundles

Taipy (and Taipy GUI) includes client-side code for web applications, written in
[TypeScript](https://www.typescriptlang.org/), and uses [React](https://reactjs.org/).
The code is packaged into JavaScript bundles that are sent to browsers when accessing
Taipy applications with a graphical interface.

There are two main JavaScript bundles to build:
- Taipy GUI: Contains the web application, the pages and all standard visual elements.
- Taipy: Contains specific visual elements for Taipy back-end functionalities
    (Scenario Management).

**Prerequisites**: To build the JavaScript bundles, ensure you have [Node.js](https://nodejs.org/)
version 18 or higher installed. Node.js includes the
[`npm` package manager](https://www.npmjs.com/).

The build process is explained in the [Taipy GUI front-end](frontend/taipy-gui/README.md) and
 [Taipy front-end](frontend/taipy/README.md) README files. Build the Taipy GUI bundle first, as
the Taipy front-end depends on it.

**Build instructions:** Run the following commands from the root directory of the repository:

```bash
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

These commands will create the `taipy/gui/webapp` and `taipy/gui_core/lib` directories in the root
folder of the taipy repository.

## Debugging the JavaScript bundles

If you plan to modify the front-end code and need to debug the TypeScript code, you must use the
following instead of the *standard* build option:
```bash
npm run build:dev
```

This will preserve the debugging symbols, and you will be able to navigate in the TypeScript code
from your debugger.

!!!note "Web application location"
    When you are developing front-end code for the Taipy GUI package, it may be cumbersome to have
    to install the package over and over when you know that all that has changed is the JavaScript
    bundle that makes the Taipy web app.

    By default, the Taipy GUI application searches for the front-end code in the
    `[taipy-gui-package-dir]/taipy/gui/webapp` directory.
    You can, however, set the environment variable `TAIPY_GUI_WEBAPP_PATH` to the location of your
    choice, and Taipy GUI will look for the web app in that directory.
    If you set this variable to the location where you build the web app repeatedly, you will no
    longer have to reinstall Taipy GUI before you try your code again.

## Running the tests

The Taipy package includes a test suite to ensure the package's functionality is correct.
The tests are written using the [pytest](https://docs.pytest.org/en/latest/) framework.
They are located in the `tests` directory of the package.

To run the tests, you need to install the required development packages. We recommend using
[Pipenv](https://pipenv.pypa.io/en/latest/) to create a virtual environment and install the
development packages.

```bash
pip install pipenv
pipenv install --dev
```

Then you can run the tests with the following command:

```bash
pipenv run pytest
```
