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
from ..data.data_node import DataNode
from ..exceptions import WrongDataNodeType
from ._file_datanode_mixin import _FileDataNodeMixin


class _DataDuplicator:
    """A service to duplicate data nodes data."""

    def __init__(self, src: DataNode):
        self.src: DataNode = src

    def can_duplicate(self) -> bool:
        """Check if the data node can be duplicated.

        Returns:
            bool: True if the data node can be duplicated, False otherwise.
        """
        return isinstance(self.src, _FileDataNodeMixin)

    def duplicate_data(self, dest: DataNode):
        """Duplicate the src data to the data of the destination data node.

        Arguments:
            dest (DataNode): The destination data node.

        Raises:
            NotImplementedError: If the data node type is not supported yet.
            WrongDataNodeType: If the source and destination data nodes have different storage types.
        """
        if isinstance(self.src, _FileDataNodeMixin):
            if self.src.storage_type() != dest.storage_type():
                raise WrongDataNodeType("Source and destination data nodes must have the same storage type.")
            self.src._duplicate_file(dest)
        else:
            raise NotImplementedError(f"Data node type '{self.src.storage_type()}' not supported for duplication yet.")
