import logging
from typing import Optional

import aiohttp

from ..models import ReportInfo


class EgressRequestService:
    async def fetch_current_bytes(self, url: str) -> Optional[bytes]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        raise ValueError(f"Failed to retrieve byte data. Status code: {response.status}")
        except Exception as e:
            logging.critical(f"Failed to retrieve byte data: Error: {e}")

    async def send_report(self, url: str, report_info: ReportInfo) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=report_info.model_dump(), headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logging.info(f"Report sent successfully: {report_info}")
                    else:
                        raise ValueError(f"Failed to send report. Status code: {response.status}")
        except Exception as e:
            logging.critical(f"Failed to send report. Status code: {e}")
