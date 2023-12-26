# Taipy GUI Extension Library example

This directory contains all the files needed to build, package and deploy an example
of a custom element library for Taipy GUI.

This example demonstrates several types of custom visual elements including static
and dynamic elements, handling properties with different types.

## Directory structure

- `README.md`: This file.
- `main.py`: A Python script that can be used to run a Taipy GUI application that
  has pages using the example element library.<br/>
  See the [section on Testing the library](#testing-the-custom-element-library) for more
  information.
- `pyproject.toml`: The Python project settings file that can be used to package
  the example library, if needed.<br/>
  See the [section on Packaging](#packaging) for more information.
- `Manifest.in`: The Python package manifest that lists the files to include or remove.<br/>
  All files that are not Python source files and that you want to be integrated into your package should
  be listed. See [Manifest.in](https://packaging.python.org/en/latest/guides/using-manifest-in/) for
  more information.
- `example_library/`: The directory where the whole extension library example is located.
   - `__init__.py`: Makes `example_library` a potential Python package.
   - `example_library.py`: The source file where the custom library is declared.
   - `front-end/`: The directory that contains all the JavaScript source files and
     build directions.
      - `package.json`: JavaScript dependency file used by `npm` to build the front-end part of
        the extension library.
      - `webpack.config.js`: This file is used for building the JavaScript bundle that
        holds the Web components code that is used in the generated pages.
      - `tsconfig.json`: The configuration file for TypeScript transpilation.
      - `src/`: The source code for the Web components used by the custom elements.
         - `index.ts`: The entry point of the generated JavaScript module.
         - `ColoredLabel.tsx`: A simple example of a React component that displays
           the value of a property as a string where each consecutive character has
           a different color.
      - `scripts/`: A directory containing NodeJS scripts used by the build process.

## Building the custom library

This section explains how to build the custom extension library.

### Prerequisites

To complete the build of the extension library, we need the following tools:

- Python 3.8 or higher;
- Taipy GUI 2.2 or higher;
- [Node.js](https://nodejs.org/en/) 18.0 or higher: a JavaScript runtime.<br/>
  This embeds [npm](https://www.npmjs.com/), the Node Package Manager.

The build process needs that you set the environment variable `TAIPY_DIR` to the location of
the Taipy installation:

- If you build from a local copy (a clone, for example) of the
  [`taipy` repository](https://github.com/Avaiga/taipy/),
  this variable should be set to the path of the directory two levels above the directory where this
  README file is located, then down to the "taipy" directory (i.e., the result of the Unix command
  "``readlink -f `pwd`/../../taipy``").
- If you are building this extension library example from an installation of Taipy GUI, you can
  get that location issuing the command `pip show taipy-gui`.

You can check that the setting is correct by verifying that the directory
"$TAIPY_DIR/taipy/gui/webapp" exists.

A way to set this variable once and for all for your environment is to add the line:
```
TAIPY_DIR=<taipy_installation_directory>
```
to the file `example_library/front-end/.env'. This file, if present, is read by the build process
to initialize the environment variable.

### Notes on configuration

This example has all the important settings, ready to be built and used to run a Taipy GUI
application using this extension or even to make it a regular Python package.

It is however important to understand the relationship between some of these settings so
that if you reuse this code, you can change some values and know what the impact of these
changes is.

- Extension Library directory: in this example, this is "example_library".<br/>
  The name of the directory where all the Python and front-end code is stored.

  - This is the name of the Python package to be imported by the Taipy GUI application
    script.<br/>
    This directory needs to hold a file called `__init__.py` so that Python recognizes this
    directory as a valid Python package directory.
  - This directory name must appear in the paths that are used in the implementation
    of the method `get_scripts()` of the `ElementLibrary` subclass. This is how
    Taipy GUI finds the JavaScript module to be loaded.
  - It is the name of the Python package to be built, as indicated in the file
    `pyproject.toml` where it appears as the value of the "name" key of the "project" table.
  - It is part of the pathname to be included when building the Python package, in
    the manifest file [`MANIFEST.in`](MANIFEST.in).

- Extension Library name: in this example, this is "example".<br/>
  The name of the extension library.

  - This name is used in the page definition texts, where in the Markdown syntax, an element
    will be defined by the `<|example.<element_name>>` fragment.
  - The name of the JavaScript module name, used as the value for `output.library.name` in
    the [webpack configuration file](example_library/front-end/webpack.config.js), is
    derived from this name if the method `get_js_module_name()` of the `ElementLibrary`
    subclass is not overloaded: the JavaScript module name defaults to a camel case version
    of the extension library name.

- Front-end code directory: in this example, this is "front-end".<br/>
  The name of the directory where all the front-end code is stored.<br/>

  - This directory name must appear in the paths that are used in the implementation
    of the method `get_scripts()` of the `ElementLibrary` subclass. This is how
    Taipy GUI finds the JavaScript module to be loaded.
  - It is part of the pathname to be included when building the Python package, in
    the manifest file [`MANIFEST.in`](MANIFEST.in).

- JavaScript bundle file name: in this example, this is "exampleLibrary.js".<br/>
  The name of the file where the front-end code is compiled.<br/>

  - It must appear in the list returned by `ElementLibrary.get_scripts()`.
  - The filename is set as the value for `output.filename` in the
    [webpack configuration file](example_library/front-end/webpack.config.js).
  - It may appear as the filename of paths included in the manifest file
    [`MANIFEST.in`](MANIFEST.in). In this example, the manifest file indicates
    that all the files located in `example_library/front-end/dist` should be
    packaged, so we don't need to explicitly refer to the bundle file name.

  Note that the path to the file also relies on the output directory setting (the
  value for `output.path`) in the
  [webpack configuration file](example_library/front-end/webpack.config.js) and
  appears also in [`MANIFEST.in`](MANIFEST.in)

- The JavaScript module name: in this example, this is "Example".<br/>
  The name of the JavaScript module.

  - This is specified as the value for `output.library.name` in the
    [webpack configuration file](example_library/front-end/webpack.config.js).
  - It is defined by overloading `ElementLibrary.get_js_module_name()`. In this example,
    we rely on the default implementation, which returns a camel case version of the element
    library name (therefore "example" is transformed to "Example").

### Building the JavaScript bundle

When all configuration files have been properly set (which is the case in this example) and
the "TAIPY_DIR" variable is set, we can build the JavaScript module file:

- Set your directory to `example_library/front-end`
- Install the Taipy GUI JavaScript bundle and the other dependencies:<br/>
  You must run the command:
  ```
  npm install
  ```
  This command will fail with a message indicating that the Taipy GUI 'webapp' directory
  could not be found if the "TAIPY_DIR" environment variable was not set properly.
- You can now build the custom element library JavaScript bundle file:
  ```
  npm run build
  ```
  This generates the bundle `exampleLibrary.js` in the `dist` directory (if you have not
  changed the `output` settings in `webpack.config.js`). This file contains the definition
  for the `Example` JavaScript module.

## Testing the custom library

Next to this README file, you can find a Python script called `main.py` that
creates a Taipy GUI application with a page that demonstrates the various
elements defined by this extension library example.

To execute this application, you can run:
```sh
python main.py
```
(prefixed by `pipenv run` if you are using `pipenv`)

## Packaging the custom library

You can create an autonomous Python package for this extension library.

The following two simple steps must be performed:

- Install the build package:
  ```sh
  pip install build
  ```
  (prefixed by `pipenv run` if you are using `pipenv`)
- Build the package:
  ```sh
  python -m build
  ```
  (prefixed by `pipenv run` if you are using `pipenv`)

This generates an autonomous Python package that contains both the back-end and the
front-end code for the extension library.

