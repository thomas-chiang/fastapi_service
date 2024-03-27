"""Services module."""

from uuid import uuid4
from typing import Iterator

from .repositories import UserRepository, BitRepository

from .models import User, Bit
import random


class BitService:
    def __init__(self, bit_repository: BitRepository) -> None:
        self._repository: BitRepository = bit_repository

    def get_current_bit(self, endpoint: str) -> bytes:
        """
        TODO: Retrieve the current bit value by making a GET request to the specified endpoint.
        """
        bits = [random.randint(0, 1) for _ in range(1024)]
        byte_array = bytearray()
        for i in range(0, 1024, 8):
            byte = 0
            for j in range(8):
                byte |= bits[i + j] << (7 - j)
            byte_array.append(byte)
        return bytes(byte_array)
    
    def save_bit(self, bit_value: bytes, timestamp: int, source: str) -> Bit:
        the_bit = Bit(bit_value=bit_value, timestamp=timestamp, source=source)
        return the_bit

    

import time

class TimeService:
    @staticmethod
    def get_current_timestamp() -> int:
        return int(time.time())



class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_users(self) -> Iterator[User]:
        return self._repository.get_all()

    def get_user_by_id(self, user_id: int) -> User:
        return self._repository.get_by_id(user_id)

    def create_user(self) -> User:
        uid = uuid4()
        return self._repository.add(email=f"{uid}@email.com", password="pwd")

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)
