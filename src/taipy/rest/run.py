from .app import create_app as _create_app


def create_app(testing=False, env=None, secret_key=None):
    """
    Create a REST application.

    Parameters:
        testing (bool): If you are on testing mode.
        env (Optional[str]): The application environment.
        secret_key (Optional[str]): Application server secret key.
    """
    return _create_app(testing, env, secret_key)


def run(app=None, **kwargs):
    """
    Build then run or run the passing application.

    Parameters:
        app (Optional[Flask]): The application to run. If None provide, the application will be created
            with default value.
        kwargs: Options to provide to the application server.
    """
    if not app:
        app = create_app()
    return app.run(**kwargs)
