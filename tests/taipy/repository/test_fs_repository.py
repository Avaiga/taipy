from dataclasses import dataclass
from queue import Queue

from dataclasses_json import dataclass_json

from taipy.repository import FileSystemRepository


@dataclass_json
@dataclass
class TestModel:
    id: str
    name: str


@dataclass
class TestObj:
    id: str
    name: str


class TestRepository(FileSystemRepository):
    def to_model(self, obj: TestObj):
        return TestModel(obj.id, obj.name)

    def from_model(self, model: TestModel):
        return TestObj(model.id, model.name)


class TestFileSystemStorage:
    def test_save_and_fetch_model(self, tmpdir):
        r = TestRepository(model=TestModel, dir_name="foo", base_path=tmpdir)
        m = TestObj("uuid", "foo")
        r.save(m)

        fetched_model = r.load(m.id)
        assert m == fetched_model

    def test_get_all(self, tmpdir):
        objs = []
        r = TestRepository(model=TestModel, dir_name="foo", base_path=tmpdir)
        for i in range(5):
            m = TestObj(f"uuid-{i}", f"Foo{i}")
            objs.append(m)
            r.save(m)
        _objs = r.load_all()

        assert len(_objs) == 5

        for obj in _objs:
            assert isinstance(obj, TestObj)
        assert sorted(objs, key=lambda o: o.id) == sorted(_objs, key=lambda o: o.id)

    def test_delete_all(self, tmpdir):
        r = TestRepository(model=TestModel, dir_name="foo", base_path=tmpdir)

        for i in range(5):
            m = TestObj(f"uuid-{i}", f"Foo{i}")
            r.save(m)

        _models = r.load_all()
        assert len(_models) == 5

        r.delete_all()
        _models = r.load_all()
        assert len(_models) == 0

    def test_search(self, tmpdir):
        r = TestRepository(model=TestModel, dir_name="foo", base_path=tmpdir)

        m = TestObj("uuid", "foo")
        r.save(m)

        m1 = r.search("name", "bar")
        m2 = r.search("name", "foo")

        assert m1 is None
        assert m == m2
