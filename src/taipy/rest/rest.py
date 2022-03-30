from .app import create_app as _create_app


class Rest:
    """
    Rest API server wrapper.
    """
    def __init__(self, testing=False, env=None, secret_key=None):
        """
        Initialise a REST API server.

        Parameters:
            testing (bool): If you are on testing mode.
            env (Optional[str]): The application environment.
            secret_key (Optional[str]): Application server secret key.
        """
        self._app = _create_app(testing, env, secret_key)

    def run(self, **kwargs):
        """
        Start a REST API server. This method is blocking.

        Parameters:
            kwargs: Options to provide to the application server.
        """
        self._app.run(**kwargs)
