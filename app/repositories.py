"""Repositories module."""
from typing import List
from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.orm import Session

from .models import User, Bit

from aioredis import Redis

class BitRepository:
    expiration_seconds = 172800 # 2 days

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def add(self, bit: Bit) -> None:
        await self._redis.setex(str(bit.timestamp)+bit.source, self.expiration_seconds ,bit.bit_value)
    
    async def get_bit_by_timestamp_and_source(self, timestamp: int, source: str) -> Bit:
        bit_value = await self._redis.get(str(timestamp)+source)
        if not bit_value:
            raise BitNotFoundError({'timestamp': timestamp, 'source': source})
        return Bit(bit_value=bit_value, source=source, timestamp=timestamp)

class NotFoundError(Exception):
    entity_name: str
    def __init__(self, entity_data):
        super().__init__(f"{self.entity_name} not found, from {entity_data}")


class BitNotFoundError(NotFoundError):
    entity_name: str = "Bit"

            









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


# class NotFoundError(Exception):

#     entity_name: str

#     def __init__(self, entity_id):
#         super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):

    entity_name: str = "User"
