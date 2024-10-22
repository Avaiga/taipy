# General contributions

Thanks for your interest in helping improve Taipy! Contributions are welcome, and they are greatly
appreciated! Every little help and credit will always be given.

There are multiple ways to contribute to Taipy: code, but also reporting bugs, creating feature
requests, helping other users in our forums, [stack**overflow**](https://stackoverflow.com/), etc.

For questions, please get in touch on [Discord](https://discord.com/invite/SJyz2VJGxV) or on GitHub
with a discussion or an issue.

## Project organisation

Taipy is organised in two main repositories:

- [taipy](https://github.com/Avaiga/taipy) is the main repository that contains the code of Taipy
    packages.
- [taipy-doc](https://github.com/Avaiga/taipy-doc) is the documentation repository.

## Never contributed to an open source project before ?

Have a look at this
[GitHub documentation](https://docs.github.com/en/get-started/quickstart/contributing-to-projects).

## Report bugs

Reporting bugs is through [GitHub issues](https://github.com/Avaiga/taipy/issues).

Please report relevant information and preferably code that exhibits the problem. We provide
templates to help you describe the issue.

The Taipy team will analyze and try to reproduce the bug to provide feedback. If confirmed,
we will add a priority to the issue and add it in our backlog. Feel free to propose a pull
request to fix it.

## Issue reporting, feedback, proposal, design or any other comment

Any feedback or proposal is greatly appreciated! Do not hesitate to create an issue with the
appropriate template on [GitHub](https://github.com/Avaiga/taipy/issues).

The Taipy team will analyse your issue and return to you as soon as possible.

## Improve Documentation

Do not hesitate to create an issue or pull request directly on the
[taipy-doc repository](https://github.com/Avaiga/taipy-doc).

# Code contributions

## Code organization

The Taipy source code is located in the [taipy](https://github.com/Avaiga/taipy)
repository, in the `taipy` directory.

Packages sources are organized in subdirectories from there:

- `taipy-common`
- `taipy-core`
- `taipy-gui`
- `taipy-rest`
- `taipy-templates`

## Process and workflow

### Issue assignment
The Taipy team manages its backlog in private. Each issue that is or is going to be engaged by the
Taipy team is attached to the "🔒 Staff only" label or has already been assigned to a Taipy team
member. Please, do not work on it, the Taipy team is on it.

All other issues are sorted by labels and are available for a contribution. If you are new to the
project, you can start with the "good first issue" or "🆘 Help wanted" label. You can also start
with issues with higher priority, like "Critical" or "High". The higher the priority, the more
value it will bring to Taipy.

If you want to work on an issue, please add a comment and wait to be assigned to the issue to
inform the community that you are working on it. Then, follow the steps below:

### Contribution workflow

1. Make your [own fork](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) of the repository
   targeted by the issue. Clone it on your local machine, then go inside the directory.

2. We are working with [Pipenv](https://github.com/pypa/pipenv) for our virtualenv.
   Create a local env and install development package by running `$ pipenv install --dev`, then
   run tests with `$ pipenv run pytest` to verify your setup.

3. For convention help, we provide a [pre-commit](https://pre-commit.com/hooks.html) file.
   This tool will run before each commit and will automatically reformat code or raise warnings
   and errors based on the code format or Python typing. You can install and set it up by doing:
   ```bash
   $ pipenv install pre-commit
   $ pipenv run python -m pre-commit install
   ```

4. Create a [pull request from your fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).<br/>
   Keep your pull request as __draft__ until your work is finished.
   Do not hesitate to add a comment for help or questions.
   Before you submit a pull request for review from your forked repo, check that it meets these
   guidelines:
     - The code and the branch name follow the
         [Taipy coding style](#coding-style-and-best-practices).
     - Include tests.
     - Code is [rebased](http://stackoverflow.com/a/7244456/1110993).
     - License is present.
     - pre-commit works - without mypy errors.
     - Taipy tests are passing.

5. The Taipy team will have a look at your Pull Request and will give feedback. If every
    requirement is valid, your work will be added in the next release, congratulations!

### Issues or Pull requests inactivity

- If your PR is not created or there is no other activity within 14 days of being assigned to
    the issue, a warning message will appear on the issue, and the issue will be marked as
    "🥶Waiting for contributor".
- If your issue is marked as "🥶Waiting for contributor", you will be unassigned after 14
    days of inactivity.
- Similarly, if there is no activity within 14 days of your PR, the PR will be marked as
    "🥶Waiting for contributor".
- If your PR is marked as "🥶Waiting for contributor", it will be closed after 14 days of
    inactivity.

We do this in order to keep our backlog moving quickly. Please don't take it personally if your
issue or PR gets closed because of this 14-day inactivity time limit. You can always reopen the
issue or PR if you're still interested in working on it.

## Coding style and best practices

### Python

Taipy's repositories follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) and
[PEP 484](https://www.python.org/dev/peps/pep-0484/) coding convention.

### TypeScript

Taipy's repositories use the [ESLint](https://eslint.org/) and
[TypeScript ESLint](https://github.com/typescript-eslint/typescript-eslint) plugin to ensure a common set of rules.

### Git branches

All new development happens in the `develop` branch. All pull requests should target that
branch. We are following a strict branch naming convention based on the pattern:
`<type>/#<issueId>[IssueSummary]`.

Where:

- `<type>` would be one of:
    - feature: new feature implementation, or improvement of a feature.
    - bug: bug fix.
    - review: change provoked by review comment not immediately taken care of.
    - refactor: refactor of a piece of code.
    - doc: doc changes (complement or typo fixes…).
    - build: in relation with the build process.
- `<issueId>` is the processed issue identifier. The advantage of explicitly indicating the issue
    number is that inGitHub, a pull request page shows a direct link to the issue description.
- `[IssueSummary]` is a short summary of the issue topic, not including spaces, using Camel case
    or lower-case, dash-separated words. This summary, with its dash (‘-’) symbol prefix, is
    optional.

## Dependency management

Taipy comes with multiple optional packages. You can find the list directly in the product or
Taipy's packages. The back-end Pipfile does not install optional packages by default due to
`pyodbc` requiring a driver's manual installation. This is not the behaviour for the front-end
that installs all optional packages through its Pipfile.

If you are a contributor on Taipy, be careful with dependencies, do not forget to install or
uninstall depending on your issue.

If you need to add a new dependency to Taipy, do not forget to add it in the `Pipfile` and the
`setup.py`. Keep in mind that dependency is a vector of attack. The Taipy team limits the usage
of external dependencies at the minimum.

## Installing the development kit

If you need the source code for Taipy on your system to see how things are done or maybe
contribute to the improvement of the packages, you can set your environment up by following
the steps below.

### Prerequisites
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

### Cloning the repository

First, clone the Taipy repository from GitHub using the following command:

```bash
git clone https://github.com/Avaiga/taipy.git
```

This creates the 'taipy' directory holding all the package's source code.

### Building the JavaScript bundles

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

The build process is explained in the
[Taipy GUI front-end](https://github.com/Avaiga/taipy/blob/develop/frontend/taipy-gui/README.md)
and
[Taipy front-end](https://github.com/Avaiga/taipy/blob/develop/frontend/taipy/README.md) README
files. Build the Taipy GUI bundle first, as the Taipy front-end depends on it.

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

### Debugging the JavaScript bundles

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

### Running the tests

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
