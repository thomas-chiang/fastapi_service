"""Models module."""

from typing import List

from pydantic import BaseModel


class ReportRequestBody(BaseModel):
    source: str
    url: str
    threshold: float
    report_url: str


class ReportInfo(BaseModel):
    channel: str
    time: int
    match_times: List[int]


class Bit(BaseModel):
    bytes: bytes
    timestamp: int
    source: str


class Score(BaseModel):
    score: float
    timestamp: int
    source: str
