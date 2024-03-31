
from ..models import Bit
from . import NotFoundError
from aioredis import Redis


class BitRepository:
    expiration_seconds = 10  # can be 2, but 10 seconds 
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