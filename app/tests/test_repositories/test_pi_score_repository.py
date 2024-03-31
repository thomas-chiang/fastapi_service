from mockfirestore import AsyncMockFirestore
import pytest
from app.repository.pi_notation_score_repository import PiNotationScoreRepository
import asyncio
from app.models import Score

@pytest.fixture(scope="module")
def firestore_db():
    return AsyncMockFirestore()

@pytest.fixture(scope="module")
def pi_notation_score_repository(firestore_db):
    return PiNotationScoreRepository(firestore_db = firestore_db)

@pytest.mark.asyncio(scope="module")
async def test_pi_notation_score_repository(pi_notation_score_repository: PiNotationScoreRepository, firestore_db: AsyncMockFirestore):
    the_score = Score(score=1, timestamp=10, source="test_pi_notation_score_repository")
    await pi_notation_score_repository.add(the_score)
    doc_snapshot = await firestore_db.collection(the_score.source).document(str(the_score.timestamp)).get()
    assert doc_snapshot.to_dict() == the_score.model_dump()

    await asyncio.gather(
        *(pi_notation_score_repository.add(Score(score=10, timestamp=timestamp, source=the_score.source)) for timestamp in range(1, 6))
    )
    the_threshold = 5
    limit = 3
    matched_scores = await pi_notation_score_repository.get_scores_larger_than_threshold(5, the_score.source, limit)
    assert len(matched_scores) <= limit
    assert all(score.score > the_threshold for score in matched_scores)

    assert len([ss async for ss in firestore_db.collection(the_score.source).stream()]) == 6
    await pi_notation_score_repository.delete_scores_before_timestamp(the_score.source, 5)
    assert len([ss async for ss in firestore_db.collection(the_score.source).stream()]) == 1