# Copyright 2021-2024 Avaiga Private Limited
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

from taipy.core import Orchestrator
from taipy.gui import Gui
from taipy.rest import Rest

if sys.version_info >= (3, 10):
    from typing import TypeGuard

_AppType = t.Union[Gui, Rest, Orchestrator]
_AppTypeT = t.TypeVar("_AppTypeT", Gui, Rest, Orchestrator)


def _run(*services: _AppType, **kwargs) -> t.Optional[Flask]:
    """Run one or multiple Taipy services.

    A Taipy service is an instance of a class that runs code as a Web application.

    Parameters:
        *services (Union[`Gui^`, `Rest^`, `Orchestrator^`]): Services to run, as separate arguments.<br/>
            If several services are provided, all the services run simultaneously.<br/>
            If this is empty or set to None, this method does nothing.
        **kwargs: Other parameters to provide to the services.
    """

    gui = __get_app(services, Gui)
    rest = __get_app(services, Rest)
    orchestrator = __get_app(services, Orchestrator)

    if gui and orchestrator:
        from taipy.core._cli._core_cli_factory import _CoreCLIFactory
        from taipy.gui._gui_cli import _GuiCLI

        _CoreCLIFactory._build_cli().create_parser()
        _GuiCLI.create_parser()

    if rest or orchestrator:
        if not orchestrator:
            orchestrator = Orchestrator()
        orchestrator.run()

    if not rest and not gui:
        return None

    if gui and rest:
        gui._set_flask(rest._app)  # type: ignore[union-attr]
        return gui.run(**kwargs)
    else:
        app = rest or gui
        assert app is not None  # Avoid pyright typing error
        return app.run(**kwargs)


if sys.version_info >= (3, 10):

    def __get_app(apps: t.Tuple[_AppType, ...], type_: t.Type[_AppTypeT]) -> t.Optional[_AppType]:
        def filter_isinstance(tl: _AppType) -> TypeGuard[_AppTypeT]:
            return isinstance(tl, type_)

        return next(filter(filter_isinstance, apps), None)
else:

    def __get_app(apps: t.Tuple[_AppType, ...], type_: t.Type[_AppTypeT]) -> t.Optional[_AppType]:
        return next(filter(lambda a: isinstance(a, type_), apps), None)
