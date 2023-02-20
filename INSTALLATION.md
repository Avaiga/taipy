# Installation

There are different ways to install Taipy GUI, depending on how
you plan to use it.

If your goal is to look into the code, modify and improve it, go straight
to the [source installation](#installing-for-development) section.

Taipy GUI needs your system to have Python 3.8 or above installed.

## Installing from PyPI

The easiest way to install Taipy GUI is from the
[Pypi software repository](https://pypi.org/project/taipy-gui/).

Run the command:
```console
$ pip install taipy-gui
```

If you are running in a virtual environment, you will have to
issue the command:
```console
$ pipenv install taipy-gui
```

These commands install the `taipy-gui` package in the Python environment
with all its dependencies.

## Installing from GitHub

The development version of Taipy GUI is updated daily with changes from the
Taipy R&D and external contributors that we praise for their input.

This development version of Taipy GUI can be installed using _pip_ and _git_:
```console
$ pip install git+https://git@github.com/Avaiga/taipy-gui
```

## Installing for development

If you need the source code for Taipy GUI on your system, so you can see
how things are done or maybe participate in the improvement of the package,
you can clone the GitHub repository:

```console
$ git clone https://github.com/Avaiga/taipy-gui.git
```

This creates the 'taipy-gui' directory that holds all the package's source code.

### Building the JavaScript bundle

Taipy GUI has some code dealing with the client side of the Web applications.
This code is written in [TypeScript](https://www.typescriptlang.org/), relies on
[React](https://reactjs.org/) components, and is packaged into a JavaScript bundle
that is sent to browsers when they connect to all Taipy GUI applications.

Here is how you can build this bundle.

You need to make sure that the [Node.js](https://nodejs.org/) JavaScript runtime version 18
or above is installed on your machine.<br/>
Note that Node.js comes with the [`npm` package manager](https://www.npmjs.com/) as part
of the standard installation.

Here is the sequence of commands that must be issued, assuming your current directory
is the root directory of the repository:

```console
# Current directory is the repository's root directory
# Move to the 'gui' directory
$ cd gui
# Install the DOM dependencies (once and for all)
$ cd dom
$ npm i
$ cd ..
# Install the Web app dependencies
$ npm i --omit=optional
# Build the Web application
$ npm run build
$ cd ..
# Current directory is the repository's root directory
```

This creates the directory `src/taipy/gui/webapp` in the root directory of the repository,
where the frontend code for Taipy GUI is split into a set of JavaScript bundles.

### Debugging the JavaScript bundle

If you plan to modify the frontend code and need to debug the TypeScript
code, you must use the following:
```
$ npm run build:dev
```

instead of the *standard* build option.

This will preserve the debugging symbols, and you will be able to navigate in the
TypeScript code from your debugger.

> **Note:** Web application location
>
> When you are developing front-end code for the Taipy GUI package, it may
> be cumbersome to have to install the package over and over when you know
> that all that has changed is the JavaScript bundle.
>
> By default, the Taipy GUI application searches for the front-end code
> in the `[taipy-gui-package-dir]/taipy/src/gui/webapp` directory.<br/>
> You can, however, set the environment variable `TAIPY_GUI_WEBAPP_PATH`
> to the location of your choice, and Taipy GUI will look for the Web
> app in that directory.<br/>
> If you set this variable to the location where you build the Web app
> repeatedly, you will no longer have to reinstall Taipy GUI before you
> try your code again.


## Running the tests

To run the tests on the package, you need to create a virtual
environment and install the development packages:

Here are the commands to issue:

```console
pipenv install --dev
pipenv run pytest
```
