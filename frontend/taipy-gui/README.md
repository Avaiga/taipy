# Taipy GUI front-end

This directory contains the source code of the Taipy GUI front-end bundle that includes the
web app and all the elements natively available in Taipy GUI.

## Prerequisites

[Node.js](https://nodejs.org/) JavaScript runtime version 18 or above must be installed on your
machine.<br/>
Note that Node.js comes with the [`npm` package manager](https://www.npmjs.com/) as part
of the standard installation.

## Build

To build the Taipy GUI bundle, you must set your current directory to this directory and then
run the following commands:

```bash
# Current directory is the directory where this README file is located:
#   [taipy-dir]/frontend/taipy-gui
#
# Install the DOM dependencies (once and for all)
cd dom
npm i
cd ..
# Install the web app dependencies
npm i --omit=optional
# Build the web app and all elements
npm run build
```


After these commands are successfully executed, a new directory will be created in
`[taipy-dir]/taipy/gui/webapp` containing all the code that the Taipy GUI front-end relies on.
