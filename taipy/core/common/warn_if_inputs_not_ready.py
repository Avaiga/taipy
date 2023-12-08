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

from typing import Iterable

from taipy.logger._taipy_logger import _TaipyLogger

from ..data import DataNode


def _warn_if_inputs_not_ready(inputs: Iterable[DataNode]):
    from ..data import CSVDataNode, ExcelDataNode, JSONDataNode, ParquetDataNode, PickleDataNode
    from ..data._data_manager_factory import _DataManagerFactory

    logger = _TaipyLogger._get_logger()
    data_manager = _DataManagerFactory._build_manager()
    for dn in inputs:
        dn = data_manager._get(dn.id)
        if dn.is_ready_for_reading is False and not dn._last_edit_date:
            if dn.storage_type() in [
                CSVDataNode.storage_type(),
                ExcelDataNode.storage_type(),
                JSONDataNode.storage_type(),
                PickleDataNode.storage_type(),
                ParquetDataNode.storage_type(),
            ]:
                logger.warning(
                    f"{dn.id} cannot be read because it has never been written. "
                    f"Hint: The data node may refer to a wrong path : {dn.path} "
                )
            else:
                logger.warning(f"{dn.id} cannot be read because it has never been written.")
