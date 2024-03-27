"""Models module."""

from sqlalchemy import Column, String, Boolean, Integer

from .database import Base

from pydantic import BaseModel, Field
from typing import List

from uuid import UUID, uuid4
from datetime import datetime


class ReportRequestBody(BaseModel):
    source: str
    end_point: str


class ReportInfo(BaseModel):
    channel: str
    time: int
    match_times: List[int]


class Bit(BaseModel):
    bit_value: bytes
    timestamp: int
    source: str
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now(datetime.UTC))


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"email=\"{self.email}\", " \
               f"hashed_password=\"{self.hashed_password}\", " \
               f"is_active={self.is_active})>"
