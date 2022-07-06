# Copyright 2022 Avaiga Private Limited
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
    Rest API server wrapper.
    """

    def __init__(self):
        """
        Initialise a REST API server.

        Parameters:
            testing (bool): If you are on testing mode.
            env (Optional[str]): The application environment.
            secret_key (Optional[str]): Application server secret key.
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
