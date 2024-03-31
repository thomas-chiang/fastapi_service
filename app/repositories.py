"""Repositories module."""

from typing import List
from contextlib import AbstractContextManager
from typing import Callable, Iterator
from google.cloud import firestore

from sqlalchemy.orm import Session

from .models import Bit, Score

from aioredis import Redis
import asyncio


class BitRepository:
    expiration_seconds = 60 * 60 * 24 * 2  # 2 days
    entity_name = "Bit"

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def add(self, bit: Bit) -> None:
        await self._redis.setex(
            name=self.entity_name + str(bit.timestamp) + bit.source, time=self.expiration_seconds, value=bit.bytes
        )

    async def get_bit_by_timestamp_and_source(self, timestamp: int, source: str) -> Bit:
        the_bytes = await self._redis.get(self.entity_name + str(timestamp) + source)
        if the_bytes == None:
            raise NotFoundError({"entity_name": self.entity_name, "timestamp": timestamp, "source": source})
        return Bit(bytes=the_bytes, source=source, timestamp=timestamp)


class ComparisonBitRepository(BitRepository):
    expiration_seconds = 60 * 60 * 24 * 2  # 2 days
    entity_name = "ComparisonBit"


class ScoreRepository:
    expiration_seconds = 60 * 60 * 24 * 2  # 2 days
    entity_name = "Score"

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def add(self, score: Score) -> None:
        await self._redis.setex(
            name=self.entity_name + str(score.timestamp) + score.source, time=self.expiration_seconds, value=score.score
        )

    async def get_score_by_timestamp_and_source(self, timestamp: int, source: str) -> Score:
        the_score = await self._redis.get(self.entity_name + str(timestamp) + source)
        if the_score == None:
            raise NotFoundError({"entity_name": self.entity_name, "timestamp": timestamp, "source": source})
        return Score(score=the_score, source=source, timestamp=timestamp)


class PiNotationScoreRepository:
    expiration_seconds = 60 * 60 * 24  # 1 days
    match_times_length = 10

    def __init__(self, firestore_db: firestore.AsyncClient) -> None:
        self._db: firestore.AsyncClient = firestore_db

    async def add(self, score: Score) -> None:
        doc_ref = self._db.collection(score.source).document(str(score.timestamp))
        await doc_ref.set(score.model_dump())

    async def delete_scores_before_timestamp(self, source: str, timestamp: int) -> None:
        doc_snapshots = [
            doc_snapshot
            async for doc_snapshot in self._db.collection(source).where("timestamp", "<=", timestamp).stream()
        ]
        await asyncio.gather(
            *(self._db.collection(source).document(doc_snapshot.id).delete() for doc_snapshot in doc_snapshots)
        )

    async def get_scores_larger_than_threshold(self, threshold: float, source: str, limit: int) -> List[Score]:
        return [
            Score(**doc_snapshot.to_dict())
            async for doc_snapshot in self._db.collection(source)
            .where("score", ">", threshold)
            .order_by("score", direction=firestore.Query.DESCENDING)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ]


class NotFoundError(Exception):
    def __init__(self, entity_data):
        super().__init__(f"entity not found, from {entity_data}")


