import asyncio
from bitarray import bitarray
from ..models import Bit
from ..repository.comparison_bit_repository import ComparisonBitRepository
from .bit_service import BitService


def bytes_to_bitarray(the_bytes: bytes) -> bitarray:
    the_bitarray = bitarray()
    the_bitarray.frombytes(the_bytes)
    return the_bitarray


def xor_bytes(byte1: bytes, byte2: bytes) -> bytes:
    bit_array1 = bytes_to_bitarray(byte1)
    bit_array2 = bytes_to_bitarray(byte2)
    return (bit_array1 ^ bit_array2).tobytes()

class ComparisonBitService(BitService):
    timestamp_interval = 60 * 60 * 24  # total seconds of one day

    @staticmethod
    async def compute_comparison_value(current_bit: Bit, previous_bit: Bit) -> bytes:
        return await asyncio.to_thread(xor_bytes, current_bit.bytes, previous_bit.bytes)

    def __init__(self, comparison_bit_repository: ComparisonBitRepository) -> None:
        self._repository: ComparisonBitRepository = comparison_bit_repository