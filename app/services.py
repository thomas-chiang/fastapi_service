"""Services module."""

import asyncio
import secrets
import time
from typing import Iterator, List
from uuid import uuid4

import aiohttp
from bitarray import bitarray

from .models import Bit, Score, User
from .repositories import (
    BitRepository,
    ComparisonBitRepository,
    NotFoundError,
    ScoreRepository,
    UserRepository,
    PiNotationScoreRepository
)


def get_random_bytes_of_length_128() -> bytes:
    return int(1).to_bytes(128, byteorder='big')
    return secrets.token_bytes(128)


def bytes_to_bitarray(the_bytes: bytes) -> bitarray:
    the_bitarray = bitarray()
    the_bitarray.frombytes(the_bytes)
    return the_bitarray


def xor_bytes(byte1: bytes, byte2: bytes) -> bytes:
    bit_array1 = bytes_to_bitarray(byte1)
    bit_array2 = bytes_to_bitarray(byte2)
    return (bit_array1 ^ bit_array2).tobytes()


def compute_score(current: bitarray, previous: bitarray, first_n: int, total_n: int) -> float:
    for i in range(first_n):
        if current[i] != previous[i]:
            return 0

    score = 0.0
    for i in range(total_n - first_n):
        score += (1024 - i) / 1024 * (current[i + first_n] == previous[i + first_n])
    return score

def compute_pi_notation_score(scores: List[Score]) -> float:
        the_value = 1
        for score in scores:
            the_value *= score.score

        return the_value



class TimeService:
    timestamp_interval = 60 * 60 * 24  # seconds of one day

    def __init__(self) -> None:
        self.current_timestamp = round(time.time())
        
    async def get_current_timestamp(self) -> int:
        return self.current_timestamp
    
    async def get_previous_day_timestamp(self) -> int:
        return self.current_timestamp - self.timestamp_interval


class BitService:
    timestamp_interval = 1  # one second
    byte_length = 1024 / 8

    @staticmethod
    async def get_current_bytes(url: str) -> bytes:
        if url == "url_for_random_bytes":
            return await asyncio.to_thread(get_random_bytes_of_length_128)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

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


class ComparisonBitService(BitService):
    timestamp_interval = 60 * 60 * 24  # total seconds of one day

    @staticmethod
    async def compute_comparison_value(current_bit: Bit, previous_bit: Bit) -> bytes:
        return await asyncio.to_thread(xor_bytes, current_bit.bytes, previous_bit.bytes)

    def __init__(self, comparison_bit_repository: ComparisonBitRepository) -> None:
        self._repository: ComparisonBitRepository = comparison_bit_repository


class ScoreService:
    timestamp_interval = 1  # one second
    first_n_bits_to_compare = 256
    total_bits = 1024
    previous_n = 4 # previous number of score to be consider
    threshold = 30



    @staticmethod
    async def compute_score(current_bit: Bit, previous_bit: Bit) -> float:
        current_bit_array, previous_bit_array = await asyncio.gather(
            asyncio.to_thread(bytes_to_bitarray, current_bit.bytes),
            asyncio.to_thread(bytes_to_bitarray, previous_bit.bytes),
        )
        return await asyncio.to_thread(
            compute_score,
            current_bit_array,
            previous_bit_array,
            ScoreService.first_n_bits_to_compare,
            ScoreService.total_bits,
        )

    def __init__(self, score_repository: ScoreRepository) -> None:
        self._repository: ScoreRepository = score_repository

    async def save_score(self, score: float, timestamp: int, source: str) -> Score:
        the_score = Score(score=score, timestamp=timestamp, source=source)
        await self._repository.add(the_score)
        return the_score

    async def previous_4_scores_exists(self, current_score: Score) -> bool:
        try:
            await self.get_previous_4_scores(current_score)
        except NotFoundError:
            return False
        return True

    async def get_previous_4_scores(self, current_score: Score) -> List[Score]:
        earliest_timestamp = current_score.timestamp - self.previous_n * self.timestamp_interval

        return await asyncio.gather(*(
            self._repository.get_score_by_timestamp_and_source(timestamp, current_score.source)
            for timestamp in range(
                earliest_timestamp,
                current_score.timestamp,
                self.timestamp_interval,
        )))


class PiNotationScoreService:
    match_times_length = 10

    @staticmethod
    async def compute_pi_notation_score(scores: List[Score]) -> float:
        return await asyncio.to_thread(compute_pi_notation_score, scores)


    def __init__(self, pi_notation_score_repository: PiNotationScoreRepository) -> None:
        self._repository: PiNotationScoreRepository = pi_notation_score_repository

    async def save_score(self, score: float, timestamp: int, source: str) -> Score:
        the_score = Score(score=score, timestamp=timestamp, source=source)
        await self._repository.add(the_score)
        return the_score
    
    async def remove_expired_pi_notation_scores(self, source: str, previous_day_timestamp: int) -> None:
        await self._repository.delete_scores_before_timestamp(source, previous_day_timestamp)

    async def get_match_times(self, threshold: float, source: int) -> List[int]:
        match_scores: List[Score] = await self._repository.get_scores_larger_than_threshold(threshold, source, self.match_times_length)
        return [match_score.timestamp for match_score in match_scores]




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


