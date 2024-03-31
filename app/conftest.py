import asyncio

import pytest
from .application import app
from fastapi.testclient import TestClient
from mockfirestore import AsyncMockFirestore

from app.repositories import  BitRepository,  PiNotationScoreRepository
from app.service.external_info_service import ExternalInfoService

from fakeredis import FakeAsyncRedis

@pytest.fixture(scope="session")
def client():
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

@pytest.fixture(scope="session")
def external_info_service():
    return ExternalInfoService()