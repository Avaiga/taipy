from __future__ import annotations
import pytest

sqlalchemy = pytest.importorskip("sqlalchemy", reason="SQLAlchemy required for ORM tests")

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from taipy.core.data.sql_table_data_node_orm import SQLAlchemyTableDataNode
from taipy.core._repository.orm_manager import ORMSessionManager


# ---------- SQLAlchemy setup ----------
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


# ---------- Pytest fixtures ----------
@pytest.fixture(scope="function")
def node(tmp_path):
    db_url = f"sqlite:///{tmp_path/'t.db'}"
    sm = ORMSessionManager(db_url)
    Base.metadata.create_all(sm.engine)
    return SQLAlchemyTableDataNode(
        config_id="user_node",
        orm_model=User,
        db_url=db_url,
        primary_keys=["id"],
    )


# ---------- Tests ----------
def test_create_and_read(node):
    node.create({"name": "Alice"})
    node.create([{"name": "Bob"}, {"name": "Chandra"}])
    rows = node.read_all()
    assert len(rows) == 3
    assert {r.name for r in rows} == {"Alice", "Bob", "Chandra"}


def test_update(node):
    node.create({"name": "Bob"})
    affected = node.update(where={"name": "Bob"}, values={"name": "Bobby"})
    assert affected == 1
    names = {r.name for r in node.read_all()}
    assert "Bobby" in names and "Bob" not in names


def test_delete(node):
    node.create([{"name": "A"}, {"name": "B"}])
    deleted = node.delete(where={"name": "A"})
    assert deleted == 1
    names = [r.name for r in node.read_all()]
    assert names == ["B"]
