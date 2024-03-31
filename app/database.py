"""Database module."""

from contextlib import contextmanager, AbstractContextManager
from typing import Callable
import logging

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


# import sys
from google.cloud import firestore
# from mockfirestore import MockFirestore  # Assuming this module exists


from typing import AsyncIterator
from aioredis import from_url, Redis


async def init_redis_pool(host: str, password: str) -> AsyncIterator[Redis]:
    session = from_url(f"redis://{host}", password=password, encoding="utf-8", decode_responses=True)
    yield session
    session.close()
    await session.wait_closed()

def init_firestore_client(project_id: str) -> firestore.AsyncClient:
    return firestore.AsyncClient(project_id)



