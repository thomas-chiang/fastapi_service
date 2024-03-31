from bitarray import bitarray
from ..models import Score, Bit
import asyncio
from ..repository.score_repository import ScoreRepository
from ..repository import NotFoundError
from typing import List


def bytes_to_bitarray(the_bytes: bytes) -> bitarray:
    the_bitarray = bitarray()
    the_bitarray.frombytes(the_bytes)
    return the_bitarray

def compute_score(current: bitarray, previous: bitarray, first_n: int, total_n: int) -> float:
    for i in range(first_n):
        if current[i] != previous[i]:
            return 0

    score = 0.0
    for i in range(total_n - first_n):
        score += (1024 - i) / 1024 * (current[i + first_n] == previous[i + first_n])
    return score

class ScoreService:
    timestamp_interval = 1  # one second
    first_n_bits_to_compare = 256
    total_bits = 1024
    previous_n = 4 # previous number of score to be consider

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