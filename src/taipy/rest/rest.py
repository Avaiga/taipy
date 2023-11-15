# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
from taipy.config import Config

from .app import create_app as _create_app


class Rest:
    """
    Runnable Rest application serving REST APIs on top of Taipy Core functionalities.
    """

    def __init__(self):
        """
        Initialize a REST API server.

        A Flask application is instantiated and configured using three parameters from the global
        config.
            - Config.global_config.testing (bool): Run the application on testing mode.
            - Config.global_config.env (Optional[str]): The application environment.
            - Config.global_config.secret_key (Optional[str]): Application server secret key.

        However, editing these parameters is only recommended for advanced users. Indeed, the default behavior of the
        REST server without any required configuration satisfies all the standard and basic needs.
        """
        self._app = _create_app(Config.global_config.testing or False, Config.global_config.env,
                                Config.global_config.secret_key)

    def run(self, **kwargs):
        """
        Start a REST API server. This method is blocking.

        Parameters:
            **kwargs : Options to provide to the application server.
        """
        self._app.run(**kwargs)
