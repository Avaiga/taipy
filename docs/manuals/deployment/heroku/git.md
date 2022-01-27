# Deploy a Taipy application based on git with Heroku

## Prerequisite

- Minimal knowledge in Git.
- Git should be installed, otherwise check [the official documentation](https://git-scm.com/downloads).
- [:material-arrow-right: Prepare your Taipy application](../prepare-taipy-for-deployment.md)
- [:material-arrow-right: Set up your Heroku environment](setup.md)

## 1. Add version control on your application

**Note:** This step is necessary only if your application doesn't already use Git.

```
git init
git config [--global] user.name "Full Name"
git config [--global] user.email "email@address.com"
git add .
git commit -m "My first commit"
```

## 2. Prepare your stack

To be able to run your app, Heroku will need the following files:

- `runtime.txt`: the version of Python you want to use. You can find the list of available version at [Heroku supported versions of Python](https://devcenter.heroku.com/articles/python-support#supported-runtimes).

    For example, put in your `runtime.txt`:
    ```
    python-3.9.10
    ```

    Now you should save this file in your git repository by doing:
    ```
    git add runtime.txt
    git commit -m "Add Heroku runtime requirement"
    ```

- `Procfile`: command launched by Heroku to start your application.

    If your entrypoint file is `main.py`, put in your `Procfile`:
    ```
    web: python main.py
    ```

    Now you should save this file in your git repository by doing:
    ```
    git add Procfile
    git commit -m "Add Heroku Procfile requirement"
    ```

- `requirements.txt`: your dependencies file. See [Virtual environments](https://docs.python.org/3/tutorial/venv.html) for details.

    **Note:** If you already have a `requirements.txt` file up to date in your Git, you can ignore this step.

    You can create this file by dumping all your dependencies then commit the file by doing:
    ```
    pip freeze > requirements.txt
    git add requirements.txt
    git commit -m "Add dependencies file"
    ```

## 3. Deployment

In our example, we use the name `my-taipy-app` for our application. On Heroku, this name should be unique. So you should replace it everywhere by a custom value.

```
heroku login
heroku create my-taipy-app
heroku git:remote -a <my-taipy-app>
heroku config:set CLIENT_URL="https://<my-taipy-app>.herokuapp.com" -a <my-taipy-app>
git push heroku main
```

**Note:** This example works if you are working on the `main` branch. If you are working on another branch
you should probably do `git push heroku my-branch:main` [check the official Heroku doc](https://devcenter.heroku.com/articles/git#deploying-from-a-branch-besides-main).

## 4. Check your deployment

You can go on the url `https://<my-taipy-app>.herokuapp.com` with your browser or run `heroku open -a <my-taipy-app>`. Your application should be deployed correctly.

## 5. Clean your resources

Remove the Heroku application: `heroku apps:destroy <my-taipy-app> --confirm <my-taipy-app>`
