# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from importlib import util
from typing import Optional


def _check_dependency_is_installed(
    module_name: str, package_name: str, extra_taipy_package_name: str, taipy_sublibrary: Optional[str] = None
) -> None:
    """
    Check if an extra package for taipy is installed.

    Args:
        module_name: Name of the taipy module importing the package.
        package_name: Name of the package.
        extra_taipy_package_name: Name of the extra taipy package.
        taipy_sublibrary: Optional name of the taipy sublibrary.

    Raises:
        RuntimeError: If the package is not installed.
    """
    if taipy_sublibrary is None:
        taipy_sublibrary = "taipy"

    if not util.find_spec(package_name):
        raise RuntimeError(
            f"Cannot use {module_name} as {package_name} package is not installed. Please install it "
            f"using `pip install {taipy_sublibrary}[{extra_taipy_package_name}]`."
        )


class EnterpriseEditionUtils:
    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core"
    _TAIPY_ENTERPRISE_EVENT_PACKAGE = _TAIPY_ENTERPRISE_MODULE + ".event"

    @classmethod
    def _using_enterprise(cls) -> bool:
        return util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None
