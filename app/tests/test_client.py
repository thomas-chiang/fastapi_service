from unittest import mock

import pytest
from aioresponses import aioresponses
from fakeredis import FakeAsyncRedis
from fastapi.testclient import TestClient
from mockfirestore import AsyncMockFirestore

from app.application import app
from app.repository.bit_repository import BitRepository
from app.repository.pi_notation_score_repository import PiNotationScoreRepository
from app.service.time_service import TimeService


@pytest.fixture(scope="module")
def client():
    with TestClient(app=app) as c:
        yield c


@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()


@pytest.fixture(scope="module")
def firestore_db():
    return AsyncMockFirestore()


@pytest.fixture(scope="module")
def bit_repository(redis):
    return BitRepository(redis=redis)


@pytest.fixture(scope="module")
def pi_notation_score_repository(firestore_db):
    return PiNotationScoreRepository(firestore_db=firestore_db)


def test_report_match_times(client, bit_repository, pi_notation_score_repository, redis):
    fake_url = "http://fake.url"
    fake_report_url = "http://fake_report.url"
    request_body = {"source": "sample_channel", "source_url": fake_url, "threshold": 100, "reporting_url": fake_report_url}

    time_service_mock = mock.Mock(spec=TimeService)
    mock_day1_curr_times = [i for i in range(1, 11)]
    mock_day2_curr_times = [day1t + 60 * 60 * 24 for day1t in mock_day1_curr_times]
    mock_curr_times = mock_day1_curr_times + mock_day2_curr_times
    mock_previous_day_times = [0] * len(mock_curr_times)

    with (
        app.container.redis_pool.override(redis),
        app.container.bit_repository.override(bit_repository),
        app.container.pi_notation_score_repository.override(pi_notation_score_repository),
    ):
        for i in range(len(mock_curr_times)):
            time_service_mock = mock.Mock(spec=TimeService)
            time_service_mock.get_current_timestamp.return_value = mock_curr_times[i]
            time_service_mock.get_previous_day_timestamp.return_value = mock_previous_day_times[i]
            with aioresponses() as mock_external_server, app.container.time_service.override(time_service_mock):
                mock_external_server.get(fake_url, body=(1).to_bytes(128, byteorder="big"), status=200)
                response = client.post("/report", json=request_body)
                assert response.status_code == 200
                data = response.json()
                assert data.get("channel") == "sample_channel"
                assert isinstance(data.get("time"), int)
                assert isinstance(data.get("match_times"), list)
                assert all(isinstance(item, int) for item in data.get("match_times"))
                if i >= 15:
                    assert data.get("match_times")
