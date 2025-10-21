from __future__ import annotations
from typing import Any, Iterable, Optional, Type, List, Dict

from taipy.core.data.data_node import DataNode
from taipy.core._repository.orm_manager import ORMSessionManager

try:
    from sqlalchemy.orm import DeclarativeMeta, Session
except Exception:  # pragma: no cover - typing fallback if SA not present
    DeclarativeMeta = Any
    Session = Any


class SQLAlchemyTableDataNode(DataNode):
    """
    ORM-enabled DataNode that maps a SQLAlchemy model (table) to a Taipy DataNode.

    Provides:
      - Simple CRUD via SQLAlchemy sessions
      - Safe returns (detached instances) so attributes are accessible after session close
      - Optional DataNode protocol bridges: read()/write()
    """

    __version__ = "0.1"

    def __init__(
        self,
        config_id: str,
        orm_model: Type[DeclarativeMeta],   # type: ignore[name-defined]
        db_url: str,
        primary_keys: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(config_id=config_id, **kwargs)
        if orm_model is None:
            raise ValueError("`orm_model` must be provided.")
        self._orm_model = orm_model
        self._primary_keys = primary_keys or []
        self._session_manager = ORMSessionManager(db_url)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _touch_all_columns(self, s: Session, objs: List[Any]) -> None:
        """Access all mapped columns while the session is active to avoid lazy refresh later."""
        if not objs:
            return
        Model = self._orm_model
        cols = [c.name for c in Model.__table__.columns]
        for obj in objs:
            _ = [getattr(obj, c) for c in cols]  # force-load attributes

    def _detach_all(self, s: Session, objs: List[Any]) -> None:
        """Detach instances from the session, making them safe to use after commit/close."""
        for obj in objs:
            s.expunge(obj)

    # ---------------------------------------------------------------------
    # CRUD METHODS
    # ---------------------------------------------------------------------
    def create(self, records: Iterable[dict] | dict) -> int:
        """
        Insert one or many records (dicts). Returns number of rows inserted.
        """
        Model = self._orm_model
        payloads = [records] if isinstance(records, dict) else list(records)
        with self._session_manager.session_scope() as s:
            s.add_all([Model(**p) for p in payloads])
            # SA will flush/commit on context exit via session_scope()
            return len(payloads)

    def read_all(self) -> List[Any]:
        """
        Return all rows as *detached* model instances.
        Attributes remain accessible after the session closes.
        """
        Model = self._orm_model
        with self._session_manager.session_scope() as s:
            results: List[Any] = list(s.query(Model).all())
            self._touch_all_columns(s, results)
            self._detach_all(s, results)
            return results

    def read_by_pk(self, **pk_values) -> Optional[Any]:
        """
        Return a single row by primary key(s) as a *detached* model instance.
        Usage:
            node.read_by_pk(id=1)                    # single PK
            node.read_by_pk(pk1=..., pk2=...)        # composite PK
        """
        if not self._primary_keys:
            raise ValueError("No primary_keys configured for this node.")
        Model = self._orm_model
        with self._session_manager.session_scope() as s:
            if len(self._primary_keys) == 1:
                obj = s.get(Model, pk_values[self._primary_keys[0]])
            else:
                key_tuple = tuple(pk_values[k] for k in self._primary_keys)
                obj = s.get(Model, key_tuple)
            if obj is None:
                return None
            self._touch_all_columns(s, [obj])
            self._detach_all(s, [obj])
            return obj

    def update(self, where: Dict[str, Any], values: Dict[str, Any]) -> int:
        """
        Update matching rows. Returns the number of affected rows.
        """
        Model = self._orm_model
        with self._session_manager.session_scope() as s:
            q = s.query(Model)
            for k, v in where.items():
                q = q.filter(getattr(Model, k) == v)
            return q.update(values, synchronize_session=False)

    def delete(self, where: Dict[str, Any]) -> int:
        """
        Delete matching rows. Returns the number of deleted rows.
        """
        Model = self._orm_model
        with self._session_manager.session_scope() as s:
            q = s.query(Model)
            for k, v in where.items():
                q = q.filter(getattr(Model, k) == v)
            count = q.count()
            q.delete(synchronize_session=False)
            return count

    # ---------------------------------------------------------------------
    # Taipy DataNode protocol bridges
    # ---------------------------------------------------------------------
    def read(self) -> List[Any]:
        return self.read_all()

    def write(self, data: Any) -> int:
        if isinstance(data, dict):
            return self.create(data)
        if isinstance(data, (list, tuple)):
            def to_dict(x):
                if isinstance(x, dict):
                    return x
                # Best-effort conversion for model-like objects
                return {k: getattr(x, k) for k in vars(x) if not k.startswith("_")}
            return self.create([to_dict(x) for x in data])
        raise TypeError("write() accepts dict or list[dict|model].")
