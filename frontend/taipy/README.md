# Taipy front-end

This directory contains the source code of the Taipy front-end bundle that includes the
Scenario Management elements.

## Prerequisites

The Taipy GUI front-end web application must have been built.<br/>
Check [this file](../taipy-gui/README.md) for more information.

## Build

To build the Taipy bundle, you must set your current directory to this directory and then
run the following commands:

```bash
# Current directory is the directory where this README file is located:
#   [taipy-dir]/frontend/taipy
#
npm i
# Build the Taipy front-end bundle
npm run build
```

After these commands are successfully executed, a new directory will be created in
`[taipy-dir]/taipy/gui_core/lib` containing all the code that implements the Taipy visual elements
for Scenario Management.
