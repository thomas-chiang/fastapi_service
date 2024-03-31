import pytest
from fakeredis import FakeAsyncRedis

from app.models import Bit, Score
from app.repository.score_repository import ScoreRepository
from app.service.score_service import ScoreService


@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()


@pytest.fixture(scope="module")
def score_repository(redis):
    return ScoreRepository(redis=redis)


@pytest.fixture(scope="module")
def score_service(score_repository):
    return ScoreService(score_repository=score_repository)


@pytest.mark.asyncio(scope="module")
async def test_score_service(score_service: ScoreService):
    the_bit = Bit(bytes=(1).to_bytes(128, byteorder="big"), timestamp=1, source="test_score_service")
    assert await score_service.compute_score(the_bit, the_bit) == sum((1024 - i) / 1024 for i in range(768))
    the_score = await score_service.save_score(1, 5, "test_score_service")
    assert Score(score=1, timestamp=5, source="test_score_service") == the_score
    the_previous_score1 = await score_service.save_score(1, 4, "test_score_service")
    the_previous_score2 = await score_service.save_score(1, 3, "test_score_service")
    the_previous_score3 = await score_service.save_score(1, 2, "test_score_service")
    assert not await score_service.previous_4_scores_exists(the_score)
    the_previous_score4 = await score_service.save_score(1, 1, "test_score_service")
    assert await score_service.previous_4_scores_exists(the_score)
    previous_n_scores = await score_service.get_previous_4_scores(the_score)
    assert the_previous_score1 in previous_n_scores
    assert the_previous_score2 in previous_n_scores
    assert the_previous_score3 in previous_n_scores
    assert the_previous_score4 in previous_n_scores
