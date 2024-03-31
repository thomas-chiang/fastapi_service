import pytest
from app.service.pi_notation_score_service import PiNotationScoreService
from app.models import Bit, Score
from app.repository.pi_notation_score_repository import PiNotationScoreRepository
from mockfirestore import AsyncMockFirestore
from unittest import mock


@pytest.fixture(scope="module")
def firestore_db():
    return AsyncMockFirestore()

@pytest.fixture(scope="module")
def pi_notation_score_repository(firestore_db):
    return PiNotationScoreRepository(firestore_db = firestore_db)

@pytest.fixture(scope="module")
def pi_notation_score_service(pi_notation_score_repository):
    return PiNotationScoreService(pi_notation_score_repository=pi_notation_score_repository)

@pytest.mark.asyncio(scope="module")
async def test_pi_notation_score_service(pi_notation_score_service: PiNotationScoreService):
    the_scores = [Score(score=2, timestamp=1, source="test_pi_notation_score_repository") for _ in range(5)]
    assert 32 == await pi_notation_score_service.compute_pi_notation_score(the_scores)

    match_time1 = 5
    match_time2 = 10
    repository_mock = mock.Mock(spec=PiNotationScoreRepository)
    repository_mock.get_scores_larger_than_threshold.return_value = [
        Score(score=3, timestamp=match_time1, source="test_pi_notation_score_service"),
        Score(score=2, timestamp=match_time2, source="test_pi_notation_score_service")
    ]
    assert [match_time1, match_time2] == await PiNotationScoreService(repository_mock).get_match_times(1, "test_pi_notation_score_service")