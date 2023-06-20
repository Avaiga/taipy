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

from taipy.core import Core
from taipy.gui import Gui
from taipy.rest import Rest

if sys.version_info >= (3, 10):
    from typing import TypeGuard

_AppType = t.Union[Gui, Rest, Core]
_AppTypeT = t.TypeVar("_AppTypeT", Gui, Rest, Core)


def _run(*services: _AppType, **kwargs) -> t.Optional[Flask]:
    """Run one or multiple Taipy services.

    A Taipy service is an instance of a class that runs code as a Web application.

    Parameters:
        *services (Union[`Gui^`, `Rest^`, `Core^`]): Services to run, as separate arguments.<br/>
            If several services are provided, all the services run simultaneously.<br/>
            If this is empty or set to None, this method does nothing.
        **kwargs: Other parameters to provide to the services.
    """

    gui = __get_app(services, Gui)
    rest = __get_app(services, Rest)
    core = __get_app(services, Core)

    if gui and core:
        from taipy.core._core_cli import _CoreCLI
        from taipy.gui._gui_cli import _GuiCLI

        _CoreCLI.create_parser()
        _GuiCLI.create_parser()

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
        assert app is not None  # Avoid pyright typing error
        return app.run(**kwargs)


# Avoid black adding too many empty lines
# fmt: off
if sys.version_info >= (3, 10):
    def __get_app(apps: t.Tuple[_AppType, ...], type_: t.Type[_AppTypeT]) -> t.Optional[_AppType]:
        def filter_isinstance(tl: _AppType) -> TypeGuard[_AppTypeT]:
            return isinstance(tl, type_)

        return next(filter(filter_isinstance, apps), None)
else:
    def __get_app(apps: t.Tuple[_AppType, ...], type_: t.Type[_AppTypeT]) -> t.Optional[_AppType]:
        return next(filter(lambda a: isinstance(a, type_), apps), None)
# fmt: on
