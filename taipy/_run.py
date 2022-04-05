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

import typing as t

from .gui import Gui
from .rest import Rest


def _run(*apps: t.List[t.Union[Gui, Rest]], **kwargs):
    """Run one or multiple Taipy services.

    A Taipy service is an instance of a class that runs code as a Web application.

    Parameters:
        *args (List[Union[`Gui^`, `Rest^`]]): Services to run. If several services are provided, all the services run simultaneously. If this is empty or set to None, this method does nothing.
        **kwargs: Other parameters to provide to the services.
    """
    gui = __typing_get(apps, Gui)
    rest = __typing_get(apps, Rest)

    if not rest and not gui:
        return

    if gui and rest:
        gui._set_flask(rest._app)
        gui.run(**kwargs)
    else:
        app = rest or gui
        app.run(**kwargs)


def __typing_get(l, type_):
    return next(filter(lambda o: isinstance(o, type_), l), None)
