# Modify the DataNode class methods
class DataNode:
    def __init__(self, name, scope, default_data=None):
        self.name = name
        self.scope = scope
        self._data = default_data
        self._editor_id = None

    def is_locked(self):
        return self._editor_id is not None

    def get_editor_id(self):
        return self._editor_id

    def lock_edit(self, editor_id=None):
        if self._editor_id is None:
            self._editor_id = editor_id

    def unlock_edit(self):
        self._editor_id = None

    def write(self, data, editor_id=None):
        if self.is_locked() and self.get_editor_id() != editor_id:
            raise DataNodeIsBeingEdited(f"DataNode is currently locked by another editor: {self.get_editor_id()}")
        # Proceed with writing data
        self._data = data

    def append(self, data, editor_id=None):
        if self.is_locked() and self.get_editor_id() != editor_id:
            raise DataNodeIsBeingEdited(f"DataNode is currently locked by another editor: {self.get_editor_id()}")
        # Proceed with appending data
        self._data.append(data)

    def read(self):
        return self._data


# Modify the FileDataNodeMixin methods
class FileDataNode(DataNode):
    def __init__(self, name, scope, path, default_data=None):
        super().__init__(name, scope, default_data)
        self.path = path

    def _upload(self, data, editor_id=None):
        if self.is_locked() and self.get_editor_id() != editor_id:
            raise DataNodeIsBeingEdited(f"DataNode is currently locked by another editor: {self.get_editor_id()}")
        # Proceed with uploading the data
        self._perform_upload(data)

    def _perform_upload(self, data):
        # Simulate the actual file upload process
        with open(self.path, 'w') as f:
            f.write(data)


# Unit Tests
import pytest

# Test the write method
def test_write_raises_exception_if_locked_by_another_editor():
    dn = DataNode("test_node", scope=Scope.GLOBAL, default_data=1)
    dn.lock_edit("editor1")
    with pytest.raises(DataNodeIsBeingEdited):
        dn.write(5, editor_id="editor2")
    dn.unlock_edit()

def test_write_allows_if_locked_by_same_editor():
    dn = DataNode("test_node", scope=Scope.GLOBAL, default_data=1)
    dn.lock_edit("editor1")
    dn.write(5, editor_id="editor1")
    assert dn.read() == 5
    dn.unlock_edit()

# Test the append method
def test_append_raises_exception_if_locked_by_another_editor():
    dn = DataNode("test_node", scope=Scope.GLOBAL, default_data=[1])
    dn.lock_edit("editor1")
    with pytest.raises(DataNodeIsBeingEdited):
        dn.append(2, editor_id="editor2")
    dn.unlock_edit()

def test_append_allows_if_locked_by_same_editor():
    dn = DataNode("test_node", scope=Scope.GLOBAL, default_data=[1])
    dn.lock_edit("editor1")
    dn.append(2, editor_id="editor1")
    assert dn.read() == [1, 2]
    dn.unlock_edit()

# Test FileDataNode _upload method
def test_file_data_node_upload_raises_exception_if_locked_by_another_editor():
    dn = FileDataNode("file_node", scope=Scope.GLOBAL, path="path/to/file")
    dn.lock_edit("editor1")
    with pytest.raises(DataNodeIsBeingEdited):
        dn._upload(data="new data", editor_id="editor2")
    dn.unlock_edit()

def test_file_data_node_upload_allows_if_locked_by_same_editor():
    dn = FileDataNode("file_node", scope=Scope.GLOBAL, path="path/to/file")
    dn.lock_edit("editor1")
    dn._upload(data="new data", editor_id="editor1")
    # Simulate file reading
    with open("path/to/file", "r") as f:
        assert f.read() == "new data"
    dn.unlock_edit()
