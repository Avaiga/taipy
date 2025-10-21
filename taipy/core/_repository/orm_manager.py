from __future__ import annotations
from contextlib import contextmanager
from typing import Generator

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
except ImportError:
    create_engine = None
    sessionmaker = None
    Session = None


class ORMNotAvailableError(ImportError):
    """Raised when SQLAlchemy is not installed."""
    pass


class ORMSessionManager:
    """Manages SQLAlchemy engine and session lifecycle."""

    def __init__(self, db_url: str, **engine_kwargs):
        """
        Initialize the ORM session manager.
        
        Args:
            db_url (str): SQLAlchemy-compatible database URL.
            **engine_kwargs: Optional engine configuration (e.g., echo=True).
        """
        if create_engine is None:
            raise ORMNotAvailableError(
                "SQLAlchemy not installed. Run: pip install 'sqlalchemy>=2,<3'"
            )

        # Create the database engine
        self._engine = create_engine(db_url, **engine_kwargs)

        # ✅ Prevent attributes from expiring after commit (fixes DetachedInstanceError)
        self._SessionLocal = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,  # crucial for stable detached objects
        )

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:  # type: ignore[name-defined]
        """
        Provide a transactional scope around a series of operations.
        
        Example:
            with ORMSessionManager("sqlite:///example.db").session_scope() as s:
                s.add(User(name="Alice"))
        """
        session: Session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def engine(self):
        """Return the SQLAlchemy engine instance."""
        return self._engine
