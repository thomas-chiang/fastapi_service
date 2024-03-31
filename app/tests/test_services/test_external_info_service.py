import pytest
from app.service.external_info_service import ExternalInfoService
from app.models import ReportInfo
from aioresponses import aioresponses
import logging

@pytest.mark.asyncio(scope="session")
async def test_fetch_current_bytes(external_info_service: ExternalInfoService, caplog):
    caplog.set_level(logging.NOTSET)
    fake_url = "http://fake_bytes.url"
    assert None == await external_info_service.fetch_current_bytes(fake_url)
    assert "Failed to retrieve byte data" in caplog.text

    mock_response = b"Mocked content"
    with aioresponses() as mock:
        mock.get(fake_url, body=mock_response, status=200)
        result = await external_info_service.fetch_current_bytes(fake_url)
        assert result == mock_response

@pytest.mark.asyncio(scope="session")
async def test_send_report(external_info_service: ExternalInfoService, caplog):
    caplog.set_level(logging.NOTSET)
    fake_url = "http://fake_report.url"
    fake_report = ReportInfo(channel="c", time=0, match_times=[0, 1, 2])
    assert None == await external_info_service.send_report(fake_url, fake_report)
    assert "Failed to send report" in caplog.text

    with aioresponses() as mock:
        mock.post(fake_url, status=200)
        await external_info_service.send_report(fake_url, fake_report)
    assert "Report sent successfully" in caplog.text