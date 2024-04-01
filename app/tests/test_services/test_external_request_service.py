import logging

import pytest
from aioresponses import aioresponses

from app.models import ReportInfo
from app.service.egress_request_service import EgressRequestService


@pytest.fixture(scope="module")
def egress_request_service():
    return EgressRequestService()


@pytest.mark.asyncio(scope="module")
async def test_fetch_current_bytes(egress_request_service: EgressRequestService, caplog):
    caplog.set_level(logging.NOTSET)
    fake_url = "http://fake_bytes.url"
    assert None is await egress_request_service.fetch_current_bytes(fake_url)
    assert "Failed to retrieve byte data" in caplog.text

    mock_response = b"Mocked content"
    with aioresponses() as mock:
        mock.get(fake_url, body=mock_response, status=200)
        result = await egress_request_service.fetch_current_bytes(fake_url)
        assert result == mock_response


@pytest.mark.asyncio(scope="module")
async def test_send_report(egress_request_service: EgressRequestService, caplog):
    caplog.set_level(logging.NOTSET)
    fake_url = "http://fake_report.url"
    fake_report = ReportInfo(channel="c", time=0, match_times=[0, 1, 2])
    assert None is await egress_request_service.send_report(fake_url, fake_report)
    assert "Failed to send report" in caplog.text

    with aioresponses() as mock:
        mock.post(fake_url, status=200)
        await egress_request_service.send_report(fake_url, fake_report)
    assert "Report sent successfully" in caplog.text
