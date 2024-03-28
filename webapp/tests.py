"""Tests module."""

from unittest import mock

import pytest
from fastapi.testclient import TestClient

from .repositories import UserRepository, UserNotFoundError
from .models import User, Bit
from .application import app
from .services import BitService, TimeService, get_random_1024_bit_value
from .database import FirestoreDatabase
from mockfirestore import MockFirestore
from .repositories import BitRepository

@pytest.fixture
def client():
    yield TestClient(app)

@pytest.fixture
def time_service():
    return TimeService()

@pytest.fixture
def firestore_database():
    return FirestoreDatabase()

@pytest.fixture
def bit_repository(firestore_database):
    return BitRepository(db = firestore_database.client)

@pytest.fixture
def bit_service(bit_repository):
    return BitService(bit_repository=bit_repository)

def test_report_match_times(client):
    request_body = {
        "source": "sample_channel",
        "end_point": "sample_endpoint"
    }
    response = client.post("/report", json=request_body)
    assert response.status_code == 200
    data = response.json()
    assert data.get('channel') == "sample_channel"
    assert isinstance(data.get('time'), int)
    assert isinstance(data.get('match_times'), list)
    assert all(isinstance(item, int) for item in data.get('match_times'))

def test_time_service(time_service):
    current_timestamp = time_service.get_current_timestamp()
    assert isinstance(current_timestamp, int)

def test_firestore_database(firestore_database):
    assert isinstance(firestore_database.client, MockFirestore)

def test_bit_repository(bit_repository, time_service, ):
    the_bit_value = get_random_1024_bit_value()
    the_timestamp = time_service.get_current_timestamp()
    the_source = "sample_source"

    bit_1 = Bit(bit_value=the_bit_value, timestamp=the_timestamp, source=the_source)
    bit_2 = Bit(bit_value=the_bit_value, timestamp=the_timestamp, source=the_source)
    bit_repository.add(bit_1)
    bit_repository.add(bit_2)
    the_bits = bit_repository.get_bits_by_timestamp_and_source(the_timestamp, the_source)
    assert len(the_bits) == 2


def test_get_bit_service(bit_service, time_service):
    the_bit_value = bit_service.get_current_bytes(endpoint="https://example.com")
    the_timestamp = 1
    the_source = "sample_source"

    previous_bit = bit_service.save_bit(
        bit_value=the_bit_value, 
        timestamp=the_timestamp, 
        source = the_source
    )

    current_bit = bit_service.save_bit(
        bit_value=the_bit_value, 
        timestamp=the_timestamp + 1, 
        source = the_source
    )

    assert len(the_bit_value) == 128  # 1024 bits = 128 bytes
    assert isinstance(current_bit, Bit)
    assert not bit_service.previous_bit_exists(previous_bit)
    assert bit_service.previous_bit_exists(current_bit)
    print(previous_bit)
    print(bit_service.get_previous_bit(current_bit))
    assert previous_bit == bit_service.get_previous_bit(current_bit)






































def test_get_list(client):
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.get_all.return_value = [
        User(id=1, email="test1@email.com", hashed_password="pwd", is_active=True),
        User(id=2, email="test2@email.com", hashed_password="pwd", is_active=False),
    ]

    with app.container.user_repository.override(repository_mock):
        response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"id": 1, "email": "test1@email.com", "hashed_password": "pwd", "is_active": True},
        {"id": 2, "email": "test2@email.com", "hashed_password": "pwd", "is_active": False},
    ]


def test_get_by_id(client):
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.get_by_id.return_value = User(
        id=1,
        email="xyz@email.com",
        hashed_password="pwd",
        is_active=True,
    )

    with app.container.user_repository.override(repository_mock):
        response = client.get("/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data == {"id": 1, "email": "xyz@email.com", "hashed_password": "pwd", "is_active": True}
    repository_mock.get_by_id.assert_called_once_with(1)


def test_get_by_id_404(client):
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.get_by_id.side_effect = UserNotFoundError(1)

    with app.container.user_repository.override(repository_mock):
        response = client.get("/users/1")

    assert response.status_code == 404


@mock.patch("webapp.services.uuid4", return_value="xyz")
def test_add(_, client):
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.add.return_value = User(
        id=1,
        email="xyz@email.com",
        hashed_password="pwd",
        is_active=True,
    )

    with app.container.user_repository.override(repository_mock):
        response = client.post("/users")

    assert response.status_code == 201
    data = response.json()
    assert data == {"id": 1, "email": "xyz@email.com", "hashed_password": "pwd", "is_active": True}
    repository_mock.add.assert_called_once_with(email="xyz@email.com", password="pwd")


def test_remove(client):
    repository_mock = mock.Mock(spec=UserRepository)

    with app.container.user_repository.override(repository_mock):
        response = client.delete("/users/1")

    assert response.status_code == 204
    repository_mock.delete_by_id.assert_called_once_with(1)


def test_remove_404(client):
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.delete_by_id.side_effect = UserNotFoundError(1)

    with app.container.user_repository.override(repository_mock):
        response = client.delete("/users/1")

    assert response.status_code == 404


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "OK"}
