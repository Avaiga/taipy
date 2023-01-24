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

import typing as t

from taipy.gui import Gui
from taipy.rest import Rest
from taipy.core import Core


def _run(*apps: t.List[t.Union[Gui, Rest, Core]], **kwargs) -> t.Optional[t.Union[Gui, Rest, Core]]:
    """Run one or multiple Taipy services.

    A Taipy service is an instance of a class that runs code as a Web application.

    Parameters:
        *args (List[Union[`Gui^`, `Rest^`, `Core^`]]): Services to run. If several services are provided, all the services run simultaneously. If this is empty or set to None, this method does nothing.
        **kwargs: Other parameters to provide to the services.
    """
    gui = __typing_get(apps, Gui)
    rest = __typing_get(apps, Rest)
    core = __typing_get(apps, Core)

    if gui and core:
        from taipy.core._version._version_cli import _VersioningCLI
        from taipy.gui._gui_cli import _GuiCLI

        _VersioningCLI._create_parser()
        _GuiCLI._create_parser()

    if rest or core:
        if not core:
            core = Core()
        core.run()

    if not rest and not gui:
        return None

    if gui and rest:
        gui._set_flask(rest._app)
        return gui.run(**kwargs)
    else:
        app = rest or gui
        return app.run(**kwargs)


def __typing_get(l, type_):
    return next(filter(lambda o: isinstance(o, type_), l), None)
