from ..models import Bit
from ..repository import NotFoundError
from ..repository.bit_repository import BitRepository

class BitService:
    timestamp_interval = 1  # one second
    byte_length = 1024 / 8

    def __init__(self, bit_repository: BitRepository) -> None:
        self._repository: BitRepository = bit_repository

    async def save_bit(self, bytes: bytes, timestamp: int, source: str) -> Bit:
        if len(bytes) != self.byte_length:
            raise ValueError(f"Incorrect byte length {len(bytes)}. Correct byte length {self.byte_length}")
        the_bit = Bit(bytes=bytes, timestamp=timestamp, source=source)
        await self._repository.add(the_bit)
        return the_bit

    async def previous_bit_exists(self, current_bit: Bit) -> bool:
        previous_timestamp = current_bit.timestamp - self.timestamp_interval
        source = current_bit.source
        try:
            await self._repository.get_bit_by_timestamp_and_source(previous_timestamp, source)
        except NotFoundError:
            return False
        return True

    async def get_previous_bit(self, current_bit: Bit) -> Bit:
        previous_timestamp = current_bit.timestamp - self.timestamp_interval
        source = current_bit.source
        return await self._repository.get_bit_by_timestamp_and_source(previous_timestamp, source)