from app.service.comparison_bit_service import ComparisonBitService
import pytest
from app.service.bit_service import BitService
from app.models import Bit
from app.repository import NotFoundError
from app.repository.comparison_bit_repository import ComparisonBitRepository
from fakeredis import FakeAsyncRedis

@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()

@pytest.fixture(scope="module")
def comparison_bit_repository(redis):
    return ComparisonBitRepository(redis = redis)

@pytest.fixture(scope="module")
def comparison_bit_service(comparison_bit_repository):
    return ComparisonBitService(comparison_bit_repository=comparison_bit_repository)


@pytest.mark.asyncio(scope="module")
async def test_comparison_bit_service(comparison_bit_service: ComparisonBitService):

    integer_one_as_byte = int(1).to_bytes(128, byteorder='big')
    integer_zero_as_byte = int(0).to_bytes(128, byteorder='big')
    previous_bit = Bit(bytes=integer_one_as_byte, timestamp=1, source="s1")
    current_bit = Bit(bytes=integer_zero_as_byte, timestamp=1, source="s1")
    result_bytes = await comparison_bit_service.compute_comparison_value(previous_bit, current_bit)
    assert integer_one_as_byte == result_bytes

    previous_comparison_bit = await comparison_bit_service.save_bit(bytes=integer_one_as_byte, timestamp=1, source="s2")
    current_comparison_bit = await comparison_bit_service.save_bit(bytes=integer_one_as_byte, timestamp=1 + 60*60*24, source="s2")
    assert await comparison_bit_service.previous_bit_exists(current_comparison_bit)
    assert previous_comparison_bit == await comparison_bit_service.get_previous_bit(current_comparison_bit)