"""Repositories module."""
from typing import List
from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.orm import Session

from .models import User, Bit
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.base_document import DocumentSnapshot
import base64


class BitRepository:
    collection_name = "bits"

    def __init__(self, db: firestore.Client) -> None:
        self.db = db

    def doc_snapshot_to_bit(self, doc_snapshot: DocumentSnapshot) -> Bit:
        doc = doc_snapshot.to_dict()
        doc["bit_value"] =  base64.b64decode(doc["bit_value"])
        return Bit(**doc)

    def add(self, bit: Bit) -> None:
        data = bit.model_dump()
        data["id"] = str(data["id"])
        data["bit_value"] = base64.b64encode(data["bit_value"]).decode('utf-8')
        doc_ref = self.db.collection(self.collection_name).document(data["id"])
        doc_ref.set(data)
    
    def get_bits_by_timestamp_and_source(self, timestamp: int, source: str) -> List[Bit]:
        query = (
            self.db.collection(self.collection_name)
            .where("timestamp", "==", timestamp)
            .where("source", "==", source)
            .stream()
        )
        return [self.doc_snapshot_to_bit(doc_snapshot) for doc_snapshot in query]

            




class UserRepository:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_all(self) -> Iterator[User]:
        with self.session_factory() as session:
            return session.query(User).all()

    def get_by_id(self, user_id: int) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(user_id)
            return user

    def add(self, email: str, password: str, is_active: bool = True) -> User:
        with self.session_factory() as session:
            user = User(email=email, hashed_password=password, is_active=is_active)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def delete_by_id(self, user_id: int) -> None:
        with self.session_factory() as session:
            entity: User = session.query(User).filter(User.id == user_id).first()
            if not entity:
                raise UserNotFoundError(user_id)
            session.delete(entity)
            session.commit()


class NotFoundError(Exception):

    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):

    entity_name: str = "User"
