# Get started for local development

## How to set up Taipy for local development.

1. Fork the [Taipy repository](https://github.com/Avaiga/taipy) on GitHub.
2. Clone your fork locally

    ```
    $ git clone git@github.com:your_name_here/taipy.git
    ```

3. Ensure [pipenv](https://pipenv.pypa.io/en/latest/) is installed.
4. Install dependencies:

    ```
    $ pipenv install --dev
    ```

5. Create a branch for local development:

    ```
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

## Make your changes locally and submit them.

1. When you're done making changes, check that your changes pass the
   tests, including testing other Python versions, with `tox`:

    ```
    $ tox
    ```

2. Commit your changes and push your branch to GitHub:

    ```
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

3. [Submit a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) through the GitHub website.

!!! info "Before you submit a pull request, check that it meets the following guidelines."

        - The pull request should include tests.
        - If the pull request adds functionality, the docs should be updated. Put
        your new functionality into a function with a docstring, and add the
        feature to the list in README.md.
        - The pull request should work for Python 3.8, 3.9 and for PyPy. Check
        https://github.com/avaiga/taipy/actions
        and make sure that the tests pass for all supported Python versions.

## Testing

Use the follonwing command to run a subset of tests.

````
    $ pytest tests.test_taipys
````
