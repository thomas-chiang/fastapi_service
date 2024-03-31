import asyncio
from contextlib import ExitStack

import pytest
from .application import app as actual_app
from fastapi.testclient import TestClient
from mockfirestore import AsyncMockFirestore

from .repositories import  BitRepository,  PiNotationScoreRepository

from fakeredis import FakeAsyncRedis
import time


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield actual_app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()




@pytest.fixture(scope="session")
def redis():
    return FakeAsyncRedis()

@pytest.fixture(scope="session")
def firestore_db():
    return AsyncMockFirestore()

@pytest.fixture(scope="session")
def bit_repository(redis):
    return BitRepository(redis = redis)

@pytest.fixture(scope="session")
def pi_notation_score_repository(firestore_db):
    return PiNotationScoreRepository(firestore_db = firestore_db)

def test_report_match_times(client, bit_repository, pi_notation_score_repository):
    # bit_repository = BitRepository(redis = FakeAsyncRedis())
    # pi_notation_score_repository = PiNotationScoreRepository(firestore_db = AsyncMockFirestore())
    request_body = {
        "source": "sample_channel",
        "url": "url_for_random_bytes",
        "threshold": 100
    }
    with actual_app.container.bit_repository.override(bit_repository), actual_app.container.pi_notation_score_repository.override(pi_notation_score_repository):
        for i in range(11):
            response = client.post("/report", json=request_body)
            time.sleep(1)
    assert response.status_code == 200
    data = response.json()
    assert data.get('channel') == "sample_channel"
    assert isinstance(data.get('time'), int)
    assert isinstance(data.get('match_times'), list)
    assert all(isinstance(item, int) for item in data.get('match_times'))

