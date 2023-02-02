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

import sys
import typing as t

from flask import Flask

from taipy.gui import Gui
from taipy.rest import Rest
from taipy.core import Core

if sys.version_info < (3, 10):
    from typing_extensions import TypeGuard
else:
    from typing import TypeGuard


def _run(*apps: t.Union[Gui, Rest, Core], **kwargs) -> t.Optional[t.Union[Gui, Rest, Core, Flask]]:
    """Run one or multiple Taipy services.

    A Taipy service is an instance of a class that runs code as a Web application.

    Parameters:
        *args (Union[`Gui^`, `Rest^`, `Core^`]): Services to run, as separate arguments.
            If several services are provided, all the services run simultaneously. If this is empty or set to None, this method does nothing.
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
        assert app is not None  # for pyright typing
        return app.run(**kwargs)


TObj = t.TypeVar("TObj", bound=t.Union[Gui, Core, Rest])


def __typing_get(tup_obj: t.Tuple[t.Union[Gui, Core, Rest], ...], type_: t.Type[TObj]) -> t.Optional[TObj]:
    def filter_isinstance(tl: t.Union[Gui, Core, Rest]) -> TypeGuard[TObj]:
        return isinstance(tl, type_)

    return next(filter(filter_isinstance, tup_obj), None)
