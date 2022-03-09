from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    from ..gui import Gui


def _varname_from_content(gui: Gui, content: str) -> t.Union[str, None]:
    return next((k for k, v in gui._get_locals_bind().items() if v == content), None)
