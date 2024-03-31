"""Database module."""

# import sys
# from mockfirestore import MockFirestore  # Assuming this module exists
from typing import AsyncIterator

from aioredis import Redis, from_url
from google.cloud import firestore


async def init_redis_pool(host: str, password: str) -> AsyncIterator[Redis]:
    session = from_url(f"redis://{host}", password=password, encoding="utf-8", decode_responses=True)
    yield session
    session.close()
    await session.wait_closed()


def init_firestore_client(project_id: str) -> firestore.AsyncClient:
    return firestore.AsyncClient(project_id)
