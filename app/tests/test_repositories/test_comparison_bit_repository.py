import pytest
from app.repository.comparison_bit_repository import ComparisonBitRepository
from app.models import Bit
from fakeredis import FakeAsyncRedis

@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()

@pytest.fixture(scope="module")
def comparison_bit_repository(redis):
    return ComparisonBitRepository(redis = redis)

@pytest.mark.asyncio(scope="module")
async def test_comparison_bit_repository(comparison_bit_repository: ComparisonBitRepository):
    the_comparison_bit = Bit(bytes=int(1).to_bytes(128, byteorder='big'), timestamp=1, source="test_comparison_bit_repository")
    await comparison_bit_repository.add(the_comparison_bit)
    assert the_comparison_bit == await comparison_bit_repository.get_bit_by_timestamp_and_source(1, "test_comparison_bit_repository")