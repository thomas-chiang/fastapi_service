import asyncio
from typing import List

from ..models import Score
from ..repository.pi_notation_score_repository import PiNotationScoreRepository


def compute_pi_notation_score(scores: List[Score]) -> float:
    the_value = 1
    for score in scores:
        the_value *= score.score

    return the_value


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
        match_scores: List[Score] = await self._repository.get_scores_larger_than_threshold(
            threshold, source, self.match_times_length
        )
        return [match_score.timestamp for match_score in match_scores]
