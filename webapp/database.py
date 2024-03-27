"""Database module."""

from contextlib import contextmanager, AbstractContextManager
from typing import Callable
import logging

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


import sys
from google.cloud import firestore
from mockfirestore import MockFirestore  # Assuming this module exists

class FirestoreDatabase:
    def __init__(self) -> None:
        if "pytest" in sys.argv[0]:
            # testing db
            self.client = MockFirestore()
        else:
            # not a testing db
            self.client = firestore.Client()  # pragma: no cover



logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
