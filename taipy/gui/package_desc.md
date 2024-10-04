# Taipy GUI

## License

Copyright 2021-2024 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions
and limitations under the License.

## What is Taipy GUI

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io). Taipy is split into multiple packages including *taipy-gui* to let users
install the minimum they need.

Taipy GUI provides Python classes that make it easy to create powerful web apps in minutes.

## Installation

There are different ways to install Taipy GUI, depending on how
you plan to use it:

- [Installing the latest release](#installing-the-latest-release)
- [Installing the development version](#installing-the-development-version)
  - [1 - Clone the repository](#1---clone-the-repository)
  - [2 - Install Node.js](#2---install-nodejs)
  - [3 - Build the JavaScript bundle](#3---build-the-javascript-bundle)
  - [4 - Install the package as editable](#4---install-the-package-as-editable)
- [Debugging the JavaScript bundle](#debugging-the-javascript-bundle)
- [Running the tests](#running-the-tests)

Taipy GUI needs your system to have **Python 3.9** or above installed.

### Installing the latest release

The easiest way to install Taipy GUI is using pip

Run the command:
```bash
pip install taipy-gui
```

### Installing the development version

The development version of Taipy GUI is updated daily with changes from the
Taipy R&D and external contributors that we praise for their input.

You should also install this version if you want to contribute to the development of Taipy GUI. Here are the steps to follow:

#### 1 - Clone the Taipy repository

Clone the Taipy repository using the following command:
```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code, and the 'taipy-gui'
source code is in the 'taipy/gui' directory.

#### 2 - Install Node.js

Taipy GUI has some code dealing with the client side of the web applications.
This code is written in <a href="https://www.typescriptlang.org/" target="_blank">TypeScript</a>, relies on <a href="https://reactjs.org/" target="_blank">React</a> components, and is packaged into a JavaScript bundle
that is sent to browsers when they connect to all Taipy GUI applications.

This bundle needs to be built before being usable by Taipy GUI.

First you need to install <a href="https://nodejs.org/" target="_blank">Node.js</a> on your system.

**Select the "Recommended For Most Users" version, and follow the instructions for your system.**

**Select "Automatically install the necessary tools" when asked.**

#### 3 - Build the JavaScript bundle

Open a new terminal and run the following commands:

- Install the DOM dependencies
```bash
cd gui
cd dom
npm i
```
- Install the web app dependencies
```bash
cd ..
npm i
```
- Build the web app
```bash
npm run build
```

After a few minutes, this creates the directory `taipy/gui/webapp` in the root directory of the repository
where the front-end code for Taipy GUI is split into a set of JavaScript bundles.

#### 4 - Install the package as editable

In a terminal, **at the root of the repository**, run:
```bash
pip install -e . --user
```

This should install the dev version of Taipy GUI as editable. You are now ready to use it.
