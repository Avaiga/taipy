# Contributions

Thanks for your interest in helping improve Taipy! Contributions are welcome, and they are greatly appreciated!
Every little help and credit will always be given.

There are multiple ways to contribute to Taipy, code, but also reporting bugs, creating feature requests, helping
other users in our forums, Stack Overflow, etc.

Today the only way to communicate with the Taipy team is by GitHub issues.

## Never contributed on an open source project before ?

Have a look on this [GitHub documentation](https://docs.github.com/en/get-started/quickstart/contributing-to-projects).

## Report bugs

Reporting bugs is through [GitHub issues](https://github.com/Avaiga/taipy/issues).

Please report relevant information and preferably code that exhibits the problem. We provide templates to help you
to present the issue in a comprehensive way.

The Taipy team will analyse and try to reproduce the bug to provide feedback. If confirmed, we will add a priority
to the issue and add it in our backlog. Feel free to propose a pull request to fix it.

## Issue reporting, feedback, proposal, design or any other comment

Any feedback or proposal is greatly appreciated! Do not hesitate to create an issue with the appropriate template on
[GitHub](https://github.com/Avaiga/taipy/issues).

The Taipy team will analyse your issue and return to you as soon as possible.

## Improve Documentation

Do not hesitate to create an issue or pull request directly on the
[taipy-doc repository](https://github.com/Avaiga/taipy-doc).

## Implement Features

The Taipy team manages its backlog in private. Each issue that will be done during our current sprint is
attached to the `current sprint`. Please, do not work on it, the Taipy team is on it.

## Code organisation

Taipy is organised in four main repositories:

- [taipy-core](https://github.com/Avaiga/taipy-core).
- [taipy-gui](https://github.com/Avaiga/taipy-gui).
- [taipy-rest](https://github.com/Avaiga/taipy-rest).
- [taipy](https://github.com/Avaiga/taipy) brings previous packages in a single one.

## Coding style and best practices

### Python

Taipy's repositories follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) and
[PEP 484](https://www.python.org/dev/peps/pep-0484/) coding convention.

## Javascript

Taipy's repositories follow the [W3Schools](https://www.w3schools.com/js/js_conventions.asp) and
[Google](https://google.github.io/styleguide/tsguide.html) coding convention.

### Git branches

All new development happens in the `develop` branch. All pull requests should target that branch.
We are following a strict branch naming convention based on the pattern: `<type>/#<issueId>[IssueSummary]`.

Where:

- `<type>` would be one of:
    - feature: new feature implementation, or improvement of a feature.
    - fix: bug fix.
    - review: change provoked by review comment not immediately taken care of.
    - refactor: refactor of a piece of code.
    - doc: doc changes (complement or typo fixes…).
    - build: in relation with the build process.
- `<issueId>` is the processed issue identifier. The advantage of explicitly indicating the issue number is that in
  GitHub, a pull request page shows a direct link to the issue description.
- `[IssueSummary]` is a short summary of the issue topic, not including spaces, using Camel case or lower-case,
  dash-separated words. This summary, with its dash (‘-’) symbol prefix, is optional.


## Contribution workflow

Find an issue without the label `current sprint` and add a comment on it to inform the community that you are
working on it.

1. Make your [own fork](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) of the repository
   target by the issue. Clone it on our local machine, then go inside the directory.

2. We are working with [Pipenv](https://github.com/pypa/pipenv) for our virtualenv.
   Create a local env and install development package by running `pipenv install --dev`, then run tests with `pipenv
   run pytest` to verify your setup.

3. For convention help, we provide a [pre-commit](https://pre-commit.com/hooks.html) file.
   This tool will run before each commit and will automatically reformat code or raise warnings and errors based on the
   code format or Python typing.
   You can install and setup it up by doing:
   ```
     pipenv install pre-commit --skip-lock
     pipenv run python -m pre-commit install
   ```

4. Make the change and create a
   [pull request from your fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).
   Keep your pull request in __draft__ until your work is finished.
   Do not hesitate to add a comment for help or questions.
   Before you submit a pull request read to review from your forked repo, check that it meets these guidelines:
    - Include tests.
    - Code is [rebase](http://stackoverflow.com/a/7244456/1110993).
    - License is present.
    - pre-commit works - without mypy error.
    - GitHub's actions are passing.

6. The taipy team will have a look at your Pull Request and will give feedback. If every requirement is valid, your
   work will be added in the next release, congratulation!


## Dependency management

Taipy comes with multiple optional packages. You can find the list directly in the product or Taipy's packages.
The back-end Pipfile does not install by default optional packages due to `pyodbc` requiring a driver's manual
installation. This is not the behaviour for the front-end that installs all optional packages through its Pipfile.

If you are a contributor on Taipy, be careful with dependencies, do not forget to install or uninstall depending on
your issue.

If you need to add to Taipy a new dependency, do not forget to add it in the `Pipfile` and the `setup.py`.
Keep in mind that dependency is a vector of attack. The Taipy team limits the usage of external dependencies at the
minimum.
