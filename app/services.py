"""Services module."""

from uuid import uuid4
from typing import Iterator

from .repositories import UserRepository, BitRepository, NotFoundError, ComparisonBitRepository

from .models import User, Bit
import random
import time
import asyncio

# class CompareValueService:
#     def __init__(self, compare_value_repository: CompareValueRepository) -> None:
#         self._repository: CompareValueRepository = compare_value_repository


def get_random_1024_bytes() -> bytes:
    bits = [random.randint(0, 1) for _ in range(1024)]
    byte_array = bytearray()
    for i in range(0, 1024, 8):
        byte = 0
        for j in range(8):
            byte |= bits[i + j] << (7 - j)
        byte_array.append(byte)
    return bytes(byte_array)

def xor_bytes(byte1: bytes, byte2: bytes) -> bytes:
    return bytes([b1 ^ b2 for b1, b2 in zip(byte1, byte2)])




class BitService:
    timestamp_interval = 1 # one second

    @staticmethod
    async def get_current_bytes(endpoint: str) -> bytes:
        """
        TODO: Retrieve the current bit value by making a GET request to the specified endpoint.
        """
        return await asyncio.to_thread(get_random_1024_bytes) 

    def __init__(self, bit_repository: BitRepository) -> None:
        self._repository: BitRepository = bit_repository       
    
    async def save_bit(self, bytes: bytes, timestamp: int, source: str) -> Bit:
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
    
    


class ComparisonBitService(BitService):
    timestamp_interval = 60 * 60 * 24 # seconds of one day

    @staticmethod
    async def compute_comparison_value(current_bit: Bit, previous_bit: Bit) -> bytes:
        return await asyncio.to_thread(xor_bytes, current_bit.bytes, previous_bit.bytes)
    
    def __init__(self, comparison_bit_repository: ComparisonBitRepository) -> None:
        self._repository: ComparisonBitRepository = comparison_bit_repository
    


class ScoreService:
    timestamp_interval = 60 * 60 * 24 # seconds of one day

    @staticmethod
    async def compute_score(current_bit: Bit, previous_bit: Bit) -> bytes:
        return await asyncio.to_thread(xor_bytes, current_bit.bytes, previous_bit.bytes)
    


class TimeService:
    @staticmethod
    async def get_current_timestamp() -> int:
        return int(await asyncio.to_thread(time.time))



class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_users(self) -> Iterator[User]:
        return self._repository.get_all()

    def get_user_by_id(self, user_id: int) -> User:
        return self._repository.get_by_id(user_id)

    def create_user(self) -> User:
        uid = uuid4()
        return self._repository.add(email=f"{uid}@email.com", password="pwd")

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)
