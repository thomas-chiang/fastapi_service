from app.application import app
import time
from aioresponses import aioresponses
from app.service.time_service import TimeService
from unittest import mock


def test_report_match_times(client, bit_repository, pi_notation_score_repository):
    fake_url = "http://fake.url"
    fake_report_url = "http://fake_report.url"
    request_body = {"source": "sample_channel", "url": fake_url, "threshold": 100, "report_url": fake_report_url}

    time_service_mock = mock.Mock(spec=TimeService)
    mock_day1_curr_times = [i for i in range(1, 11)]
    mock_day2_curr_times = [day1t + 60*60*24 for day1t in mock_day1_curr_times]
    mock_curr_times = mock_day1_curr_times+mock_day2_curr_times
    mock_previous_day_times = [0]* len(mock_curr_times)

    with (
        app.container.bit_repository.override(bit_repository), 
        app.container.pi_notation_score_repository.override(pi_notation_score_repository),
    ):
        for i in range(len(mock_curr_times)):
            time_service_mock = mock.Mock(spec=TimeService)
            time_service_mock.get_current_timestamp.return_value = mock_curr_times[i]
            time_service_mock.get_previous_day_timestamp.return_value = mock_previous_day_times[i]
            with (
                aioresponses() as mock_external_server,
                app.container.time_service.override(time_service_mock)
            ):
                mock_external_server.get(fake_url, body=int(1).to_bytes(128, byteorder='big'), status=200)
                response = client.post("/report", json=request_body)
                assert response.status_code == 200
                data = response.json()
                assert data.get("channel") == "sample_channel"
                assert isinstance(data.get("time"), int)
                assert isinstance(data.get("match_times"), list)
                assert all(isinstance(item, int) for item in data.get("match_times"))
                if i >= 15:
                    assert data.get("match_times")
