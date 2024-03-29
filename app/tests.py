"""Tests module."""

from unittest import mock

import pytest
from fastapi.testclient import TestClient

from .repositories import UserRepository, UserNotFoundError
from .models import User, Bit
from .application import app
from .services import BitService, TimeService, get_random_1024_bytes, ComparisonBitService
from .repositories import BitRepository, ComparisonBitRepository

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
def bit_repository(redis):
    return BitRepository(redis = redis)

@pytest.fixture
def comparison_bit_repository(redis):
    return ComparisonBitRepository(redis = redis)

@pytest.fixture
def bit_service(bit_repository):
    return BitService(bit_repository=bit_repository)

@pytest.fixture
def comparison_bit_service(comparison_bit_repository):
    return ComparisonBitService(comparison_bit_repository=comparison_bit_repository)




def test_report_match_times(client, bit_repository):
    request_body = {
        "source": "sample_channel",
        "end_point": "sample_endpoint"
    }
    with app.container.bit_repository.override(bit_repository):
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


@pytest.mark.asyncio
async def test_bit_repository(bit_repository: BitRepository, time_service: TimeService):
    the_bytes = get_random_1024_bytes()
    the_timestamp = await time_service.get_current_timestamp()
    the_source = "sample_source"

    bit_1 = Bit(bytes=the_bytes, timestamp=the_timestamp, source=the_source)
    await bit_repository.add(bit_1)
    the_bit = await bit_repository.get_bit_by_timestamp_and_source(the_timestamp, the_source)
    assert bit_1 == the_bit


@pytest.mark.asyncio
async def test_comparison_bit_repository(comparison_bit_repository: ComparisonBitRepository, time_service: TimeService):
    the_bytes = get_random_1024_bytes()
    the_timestamp = await time_service.get_current_timestamp()
    the_source = "sample_source"

    bit_1 = Bit(bytes=the_bytes, timestamp=the_timestamp, source=the_source)
    await comparison_bit_repository.add(bit_1)
    the_bit = await comparison_bit_repository.get_bit_by_timestamp_and_source(the_timestamp, the_source)
    assert bit_1 == the_bit


@pytest.mark.asyncio
async def test_bit_service(bit_service: BitService):
    the_bytes = await bit_service.get_current_bytes(endpoint="https://example.com")
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
    assert await bit_service.previous_bit_exists(current_bit)
    assert previous_bit == await bit_service.get_previous_bit(current_bit)


@pytest.mark.asyncio
async def test_comparison_bit_service(comparison_bit_service: ComparisonBitService, redis: FakeAsyncRedis):

    """
    test compute_comparison_value
    """
    integer_one_as_byte = int(1).to_bytes(1, byteorder='big')
    integer_zero_as_byte = int(0).to_bytes(1, byteorder='big')
    previous_bit = Bit(bytes=integer_one_as_byte, timestamp=1, source="s1")
    current_bit = Bit(bytes=integer_zero_as_byte, timestamp=1, source="s1")
    result_bytes = await comparison_bit_service.compute_comparison_value(previous_bit, current_bit)
    assert integer_one_as_byte == result_bytes

    previous_comparison_bit = await comparison_bit_service.save_bit(bytes=bytes(), timestamp=1, source="s2")
    current_comparison_bit = await comparison_bit_service.save_bit(bytes=bytes(), timestamp=1 + 60*60*24, source="s2")
    assert await comparison_bit_service.previous_bit_exists(current_comparison_bit)
    assert previous_comparison_bit == await comparison_bit_service.get_previous_bit(current_comparison_bit)
































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
