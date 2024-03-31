import logging

import pytest
from aioresponses import aioresponses

from app.models import ReportInfo
from app.service.external_request_service import ExternalRequestService


@pytest.fixture(scope="module")
def external_request_service():
    return ExternalRequestService()


@pytest.mark.asyncio(scope="module")
async def test_fetch_current_bytes(external_request_service: ExternalRequestService, caplog):
    caplog.set_level(logging.NOTSET)
    fake_url = "http://fake_bytes.url"
    assert None is await external_request_service.fetch_current_bytes(fake_url)
    assert "Failed to retrieve byte data" in caplog.text

    mock_response = b"Mocked content"
    with aioresponses() as mock:
        mock.get(fake_url, body=mock_response, status=200)
        result = await external_request_service.fetch_current_bytes(fake_url)
        assert result == mock_response


@pytest.mark.asyncio(scope="module")
async def test_send_report(external_request_service: ExternalRequestService, caplog):
    caplog.set_level(logging.NOTSET)
    fake_url = "http://fake_report.url"
    fake_report = ReportInfo(channel="c", time=0, match_times=[0, 1, 2])
    assert None is await external_request_service.send_report(fake_url, fake_report)
    assert "Failed to send report" in caplog.text

    with aioresponses() as mock:
        mock.post(fake_url, status=200)
        await external_request_service.send_report(fake_url, fake_report)
    assert "Report sent successfully" in caplog.text
