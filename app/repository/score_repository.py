from aioredis import Redis

from ..models import Score
from . import NotFoundError


class ScoreRepository:
    expiration_seconds = 60  # can be 10, but 60 seconds for buffer
    entity_name = "Score"

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def add(self, score: Score) -> None:
        await self._redis.setex(
            name=self.entity_name + str(score.timestamp) + score.source, time=self.expiration_seconds, value=score.score
        )

    async def get_score_by_timestamp_and_source(self, timestamp: int, source: str) -> Score:
        the_score = await self._redis.get(self.entity_name + str(timestamp) + source)
        if the_score is None:
            raise NotFoundError({"entity_name": self.entity_name, "timestamp": timestamp, "source": source})
        return Score(score=the_score, source=source, timestamp=timestamp)
