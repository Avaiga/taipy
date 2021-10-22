from dataclasses import dataclass

from dataclasses_json import dataclass_json

from taipy.repository import FileSystemRepository


@dataclass_json
@dataclass
class TestModel:
    id: str
    name: str


class TestFileSystemStorage:
    def test_save_and_fetch_model(self, tmpdir):
        r = FileSystemRepository(model=TestModel, dir_name="foo", base_path=tmpdir)
        m = TestModel("uuid", "foo")
        r.save(m)

        fetched_model = r.get(m.id)
        assert m == fetched_model

    def test_get_all(self, tmpdir):
        r = FileSystemRepository(model=TestModel, dir_name="foo", base_path=tmpdir)
        for i in range(5):
            m = TestModel(f"uuid-{i}", f"Foo{i}")
            r.save(m)
        _models = r.get_all()

        assert len(_models) == 5

        for obj in _models:
            assert isinstance(obj, TestModel)

    def test_delete_all(self, tmpdir):
        r = FileSystemRepository(model=TestModel, dir_name="foo", base_path=tmpdir)

        for i in range(5):
            m = TestModel(f"uuid-{i}", f"Foo{i}")
            r.save(m)

        _models = r.get_all()
        assert len(_models) == 5

        r.delete_all()
        _models = r.get_all()
        assert len(_models) == 0

    def test_search(self, tmpdir):
        r = FileSystemRepository(model=TestModel, dir_name="foo", base_path=tmpdir)

        m = TestModel("uuid", "foo")
        r.save(m)

        m1 = r.search("name", "bar")
        m2 = r.search("name", "foo")

        assert m1 is None
        assert m == m2
