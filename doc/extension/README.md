# Taipy GUI Extension template

This directory contains all the files needed to build, package and deploy a custom element
library for Taipy GUI: all the files that are needed to create a library and its elements,
as well as what is needed to build a standalone Python package that can be distributed.

The files provided in this directory implement a custom element library that contains a
very basic dynamic custom element. Using this template, you can get started with the build
process involving both Python and JavaScript source code.

## Directory structure

- `README.md`: This file.
- `demo.py`: A Python script that can be used to demonstrate the custom
  element library.<br/>
  See the [section on Testing the library](#testing-the-custom-element-library) for more
  information.
- `setup.py`: A Python script that is used to package the extension library, if
  needed.<br/>
  See the [section on Packaging](#packaging) for more information.
- `find_taipy_gui_dir.py`: Locates the absolute path of the installation directory for
  Taipy GUI. This is used to customize the build of the JavaScript bundle.<br/>
  See the [Building the JavaScript bundle](#building-the-javascript-bundle) section to
  learn when this may be useful.
- `Manifest.in`: The Python package manifest that lists the files to include or remove.
  All files that are not Python source files and that you want integrated in your package should be listed.
  See [Manifest.in](https://packaging.python.org/en/latest/guides/using-manifest-in/) for more information.
- `Pipfile`: Lists the Python package dependencies used by [`pipenv`](https://pypi.org/project/pipenv/).
- `my_custom_lib/`: The directory where the whole extension library is located.
   - `__init__.py`: Makes the `my_custom_lib` a potential Python package.
   - `my_library.py`: The source file where the custom library is declared.
   - `webui/`: The directory that contains all the JavaScript source files and
     build directions.
      - `package.json`: JavaScript dependency file used by npm.<br/>
        This file is updated when you manually install Taipy GUI.
      - `webpack.config.js`: This file is used for building the JavaScript bundle that
        holds the Web components code that is used in the generated pages.
      - `tsconfig.json`: We are using [TypeScript](https://www.typescriptlang.org/)
        as a more productive language, compared to JavaScript, to create the Web
        components that are rendered on the generated pages. The TypeScript
        transpiler (the program that transforms TypeScript code to vanilla JavaScript)
        needs this file to drive its execution.
      - `src/`: The source code for the Web components used by the custom elements.
         - `index.ts`: The entry point of the generated JavaScript module.
         - `SimpleLabel.tsx`: A simple example of a React component that displays
           the value of a property.
   
## Building the custom library

This section explains how to build the custom extension library.

### Prerequisites

To complete the build of the extension library, we need to following tools:

- Python 3.8 or higher;
- Taipy GUI 2.0 or higher;
- [Node.js](https://nodejs.org/en/) 16.x or higher: a JavaScript runtime.<br/>
  This embeds [npm](https://www.npmjs.com/), the Node Package Manager.

Installing Taipy GUI is usually done in a Python virtual environment.

Create a command prompt (shell) and set to current directory to the `my_custom_lib`
sitting next to this README file.

- If you are using `pipenv`:
   ```sh
   $ pipenv --python $PYTHON_VERSION
   $ pipenv shell
   $ pipenv install
   ```

- If you are not using `pipenv`:
   ```sh
   $ pip install virtualenv
   $ python -m venv ./venv
   $ source ./venv/bin/activate
   $ pip install taipy-gui
   ```

### Customize the build process

You will need to adapt some files in this template directory to match your specific
needs. Here are the important settings that you must check:

- `my_custom_lib/webui/webpack.config.js`: This file is used to compile all the JavaScript
  code into a single JavaScript bundle.<br/>
  Here are the settings that you must check:
  - `output.path` and `output.filename`: These indicate the location and the name of the
    generated JavaScript bundle file.<br/>
    If you want to change any of these parameters, you must make sure that the location
    and filename that you have set are reflected in the list of mandatory scripts declared
    by the element library code: in `my_custom_lib/my_library.py`, the method
    `get_script()` must return an array where the path to this script is explicitly
    indicated, relative to the element library source file.<br/>
    A new setting of `output.path` must also be reflected in
    `my_custom_lib/webui/tsonfig.js` (see below).
    The default values are set to generate the file `myLibrary.js` in the `dist` directory
    (located in the `webui` directory, where the bundle is built).
  - `output.library.name`: Indicates the name of the JavaScript module that holds the code
    for the generated library.</br>
    It must be derived from the name of the element library (the value of the `get_name()`
    method for the custom library in `my_custom_lib/my_library.py`): the name of the
    JavaScript object should be a camel case version of the library name.<br/>
    If `get_name()` returns `"the_name_of_the_library"` then this setting should be set
    to `"TheNameOfTheLibrary"`.
  - `plugins`: We must provide `webpack` with the path to a bundle, provided by Taipy GUI,
    that holds all the dependencies that Taipy GUI depends on.<br/>
    You must set the `manifest` argument to
    `<TAIPY_GUI_DIR>/webapp/taipy-gui-deps-manifest.json` where `<TAIPY_GUI_DIR>` is the 
    absolute path to the Taipy GUI installation directory, as returned by the script
    `find_taipy_gui_dir.py`.
- `my_custom_lib/webui/tsonfig.json`:
   - `"outDir"`: Must be set to the value of `output.path` in
     `my_custom_lib/webui/webpack.config.js`.
   - `"include"`: Must have the item indicating where the TypeScript source files should
     be located. The default is `"src"`, referencing `my_custom_lib/webui/src`.

### Things to check

The previous section explained what to change and where.
Another way of looking at things is to list the different settings that can be
modified, and check that they all match:

- The element library name: set by overriding `ElementLibrary.get_name()`.<br/>
  This is the prefix that is used in page description texts to find the visual
  element to instantiate.
- The JavaScript module name: Is specified in `webpack.config.js` (setting is
  `output.library.name`).<br/>
  By default, it is a camel case version of the element library name.<br/>
  It can be specified otherwise by overriding `ElementLibrary.get_js_module_name()`.
- The JavaScript bundle path name: Is specified in `webpack.config.js` (settings are
  `output.filename` and `output.path`).<br/>
  This is the path of the file that contains all the JavaScript parts of the library. It
  must appear in the list returned by `ElementLibrary.get_scripts()`.
- The element names: They are declared as keys to the dictionary returned by 
  `ElementLibrary.get_elements()`.<br/>
  They are used to find an element in a library when the page description text is
  read.
- The element component names: Are specified as the value of the `react_component`
  argument to the `Element` constructor.<br/>
  These component names must be exported with the exact same name from the JavaScript
  bundle entry point.

### Building the JavaScript bundle

When all configuration files have been properly updated, we can build the
JavaScript bundle:

- Set your directory to `my_custom_lib/webui`
- Install the Taipy GUI JavaScript bundle:<br/>
  You must run the command:
  ```
  npm i $TAIPY_GUI_DIR/webapp
  ```
  (or `npm i %TAIPY_GUI_DIR%/webapp` on Windows machines)

  where the variable TAIPY_GUI_DIR represents the absolute path to the installation
  of Taipy GUI, on your filesystem. You can use the script `find_taipy_gui_dir.py`
  that will find this location.
- You can now build the custom element library JavaScript bundle file:
  ```
  npm run build
  ```
  This generates the bundle `myCustom.js` in the `dist` directory (if you have not changed
  the `output` settings in `webpack.config.js`).

### Testing the custom element library

If you now go back to the top directory, you will find the Python script `demo.py`
that shows how to integrate the new element into a regular Taipy application.

To execute this application, you can run:
   ```bash
   # With pipenv
   pipenv run python demo.py
    
   # Without pipenv
   python  demo.py
   ```

And see the custom label control in action.

### Packaging

You can create an autonomous Python package to distribute your Taipy GUI custom extension library.

The following steps must be performed:

- Install the build package:
  - If you are using `pipenv`:
  ```
  $ pipenv run pip install build
  ```
- If you are not using `pipenv`:
  ```
  $ pip install build
  ```
- Configure the file `setup.py` to match your settings:

  - The `name` parameter must be set to the package name, which contains the Taipy GUI
    Extension library.<br/>
    Note that before you pick a name for your package, you should make sure that it has not
    already being used. The name of the package is not related to the `import` directive
    in your Python code.
  - The `author` and `author_email` parameters should be set to the package author name
    and email address.
  - The `description` and `long_description` parameters should provide a description of
    this package (short and long versions).
  - The `keywords` parameter should hold relevant keywords exposed by Pypi.
  - The `packages` parameter indicates which directories and files should be included in
    this package.<br/>
    If you have renamed the extension library root directory, you will need to update this,
    replacing "my_custom_lib" with the name of the directory you have created.
  - The `version` parameter should reflect the extension library version you are packaging.
  - Check the `classifiers` and `license` parameters.

- Build the package:
   ```bash
   # With pipenv
   pipenv run python -m build
    
   # Without pipenv
   python -m build
   ```

This generates a Python package that can be uploaded to Pipy or shared with community
members.

