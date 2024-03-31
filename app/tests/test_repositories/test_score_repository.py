import pytest
from app.models import Score
from app.repository.score_repository import ScoreRepository
from fakeredis import FakeAsyncRedis

@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()

@pytest.fixture(scope="module")
def score_repository(redis):
    return ScoreRepository(redis = redis)

@pytest.mark.asyncio(scope="module")
async def test_score_repository(score_repository: ScoreRepository):
    the_score = Score(score=1, timestamp=1, source="test_score_repository")
    await score_repository.add(the_score)
    assert the_score == await score_repository.get_score_by_timestamp_and_source(1, "test_score_repository")