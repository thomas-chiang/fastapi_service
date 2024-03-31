"""Tests module."""
import asyncio
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from mockfirestore import AsyncMockFirestore

from .models import User, Bit, Score
from .application import app
from .services import BitService, TimeService, get_random_bytes_of_length_128, ComparisonBitService, ScoreService, PiNotationScoreService
from .repositories import UserRepository, UserNotFoundError, BitRepository, ComparisonBitRepository, NotFoundError, ScoreRepository, PiNotationScoreRepository
from unittest import mock

from fakeredis import FakeAsyncRedis

@pytest.fixture
def client():
    yield TestClient(app)

@pytest.fixture
def time_service():
    return TimeService()

@pytest.fixture
def redis():
    return FakeAsyncRedis()

@pytest.fixture
def firestore_db():
    return AsyncMockFirestore()

@pytest.fixture
def bit_repository(redis):
    return BitRepository(redis = redis)

@pytest.fixture
def comparison_bit_repository(redis):
    return ComparisonBitRepository(redis = redis)

@pytest.fixture
def score_repository(redis):
    return ScoreRepository(redis = redis)

@pytest.fixture
def pi_notation_score_repository(firestore_db):
    return PiNotationScoreRepository(firestore_db = firestore_db)

@pytest.fixture
def bit_service(bit_repository):
    return BitService(bit_repository=bit_repository)

@pytest.fixture
def comparison_bit_service(comparison_bit_repository):
    return ComparisonBitService(comparison_bit_repository=comparison_bit_repository)

@pytest.fixture
def score_service(score_repository):
    return ScoreService(score_repository=score_repository)

@pytest.fixture
def pi_notation_score_service(pi_notation_score_repository):
    return PiNotationScoreService(pi_notation_score_repository=pi_notation_score_repository)


def test_report_match_times(client: TestClient, bit_repository: BitRepository, pi_notation_score_repository: PiNotationScoreRepository):
    request_body = {
        "source": "sample_channel",
        "url": "url_for_random_bytes",
        "threshold": 100
    }
    with app.container.bit_repository.override(bit_repository), app.container.pi_notation_score_repository.override(pi_notation_score_repository):
        response = client.post("/report", json=request_body)
    assert response.status_code == 200
    data = response.json()
    assert data.get('channel') == "sample_channel"
    assert isinstance(data.get('time'), int)
    assert isinstance(data.get('match_times'), list)
    assert all(isinstance(item, int) for item in data.get('match_times'))


@pytest.mark.asyncio
async def test_time_service(time_service: TimeService):
    current_timestamp = await time_service.get_current_timestamp()
    assert isinstance(current_timestamp, int)
    assert current_timestamp - 60*60*24 == await time_service.get_previous_day_timestamp()


@pytest.mark.asyncio
async def test_bit_repository(bit_repository: BitRepository,):
    the_bit = Bit(bytes=get_random_bytes_of_length_128(), timestamp=1, source="test_bit_repository")
    await bit_repository.add(the_bit)
    assert the_bit == await bit_repository.get_bit_by_timestamp_and_source(1, "test_bit_repository")


@pytest.mark.asyncio
async def test_comparison_bit_repository(comparison_bit_repository: ComparisonBitRepository):
    the_comparison_bit = Bit(bytes=get_random_bytes_of_length_128(), timestamp=1, source="test_comparison_bit_repository")
    await comparison_bit_repository.add(the_comparison_bit)
    assert the_comparison_bit == await comparison_bit_repository.get_bit_by_timestamp_and_source(1, "test_comparison_bit_repository")


@pytest.mark.asyncio
async def test_score_repository(score_repository: ScoreRepository):
    the_score = Score(score=1, timestamp=1, source="test_score_repository")
    await score_repository.add(the_score)
    assert the_score == await score_repository.get_score_by_timestamp_and_source(1, "test_score_repository")

@pytest.mark.asyncio
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



@pytest.mark.asyncio
async def test_bit_service(bit_service: BitService):
    with pytest.raises(Exception):
        await bit_service.get_current_bytes(url="https://wrong_url")

    the_bytes = await bit_service.get_current_bytes(url="url_for_random_bytes")
    the_timestamp = 1
    the_source = "sample_source"

    previous_bit = await bit_service.save_bit(
        bytes=the_bytes, 
        timestamp=the_timestamp, 
        source = the_source
    )

    current_bit = await bit_service.save_bit(
        bytes=the_bytes, 
        timestamp=the_timestamp + 1, 
        source = the_source
    )

    assert len(the_bytes) == 128  # 1024 bits = 128 bytes
    assert isinstance(current_bit, Bit)
    assert not await bit_service.previous_bit_exists(previous_bit)
    with pytest.raises(NotFoundError):
        await bit_service.get_previous_bit(previous_bit)

    assert await bit_service.previous_bit_exists(current_bit)
    assert previous_bit == await bit_service.get_previous_bit(current_bit)

    with pytest.raises(ValueError, match=r"Incorrect byte length \d+. Correct byte length \d+"):
        await bit_service.save_bit(b"1", the_timestamp, the_source)


@pytest.mark.asyncio
async def test_comparison_bit_service(comparison_bit_service: ComparisonBitService):

    integer_one_as_byte = int(1).to_bytes(128, byteorder='big')
    integer_zero_as_byte = int(0).to_bytes(128, byteorder='big')
    previous_bit = Bit(bytes=integer_one_as_byte, timestamp=1, source="s1")
    current_bit = Bit(bytes=integer_zero_as_byte, timestamp=1, source="s1")
    result_bytes = await comparison_bit_service.compute_comparison_value(previous_bit, current_bit)
    assert integer_one_as_byte == result_bytes

    previous_comparison_bit = await comparison_bit_service.save_bit(bytes=integer_one_as_byte, timestamp=1, source="s2")
    current_comparison_bit = await comparison_bit_service.save_bit(bytes=integer_one_as_byte, timestamp=1 + 60*60*24, source="s2")
    assert await comparison_bit_service.previous_bit_exists(current_comparison_bit)
    assert previous_comparison_bit == await comparison_bit_service.get_previous_bit(current_comparison_bit)


@pytest.mark.asyncio
async def test_score_service(score_service: ScoreService):
    the_bit = Bit(bytes=get_random_bytes_of_length_128(), timestamp=1, source="test_score_service")
    assert await score_service.compute_score(the_bit, the_bit) == sum(((1024-i)/1024 for i in range(768)))
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



@pytest.mark.asyncio
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


























# def test_get_list(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.get_all.return_value = [
#         User(id=1, email="test1@email.com", hashed_password="pwd", is_active=True),
#         User(id=2, email="test2@email.com", hashed_password="pwd", is_active=False),
#     ]

#     with app.container.user_repository.override(repository_mock):
#         response = client.get("/users")

#     assert response.status_code == 200
#     data = response.json()
#     assert data == [
#         {"id": 1, "email": "test1@email.com", "hashed_password": "pwd", "is_active": True},
#         {"id": 2, "email": "test2@email.com", "hashed_password": "pwd", "is_active": False},
#     ]


# def test_get_by_id(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.get_by_id.return_value = User(
#         id=1,
#         email="xyz@email.com",
#         hashed_password="pwd",
#         is_active=True,
#     )

#     with app.container.user_repository.override(repository_mock):
#         response = client.get("/users/1")

#     assert response.status_code == 200
#     data = response.json()
#     assert data == {"id": 1, "email": "xyz@email.com", "hashed_password": "pwd", "is_active": True}
#     repository_mock.get_by_id.assert_called_once_with(1)


# def test_get_by_id_404(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.get_by_id.side_effect = UserNotFoundError(1)

#     with app.container.user_repository.override(repository_mock):
#         response = client.get("/users/1")

#     assert response.status_code == 404


# @mock.patch("webapp.services.uuid4", return_value="xyz")
# def test_add(_, client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.add.return_value = User(
#         id=1,
#         email="xyz@email.com",
#         hashed_password="pwd",
#         is_active=True,
#     )

#     with app.container.user_repository.override(repository_mock):
#         response = client.post("/users")

#     assert response.status_code == 201
#     data = response.json()
#     assert data == {"id": 1, "email": "xyz@email.com", "hashed_password": "pwd", "is_active": True}
#     repository_mock.add.assert_called_once_with(email="xyz@email.com", password="pwd")


# def test_remove(client):
#     repository_mock = mock.Mock(spec=UserRepository)

#     with app.container.user_repository.override(repository_mock):
#         response = client.delete("/users/1")

#     assert response.status_code == 204
#     repository_mock.delete_by_id.assert_called_once_with(1)


# def test_remove_404(client):
#     repository_mock = mock.Mock(spec=UserRepository)
#     repository_mock.delete_by_id.side_effect = UserNotFoundError(1)

#     with app.container.user_repository.override(repository_mock):
#         response = client.delete("/users/1")

#     assert response.status_code == 404


# def test_status(client):
#     response = client.get("/status")
#     assert response.status_code == 200
#     data = response.json()
#     assert data == {"status": "OK"}
