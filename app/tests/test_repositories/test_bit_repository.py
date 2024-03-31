import pytest
from app.models import Bit
from app.repository.bit_repository import BitRepository
from fakeredis import FakeAsyncRedis

@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()

@pytest.fixture(scope="module")
def bit_repository(redis):
    return BitRepository(redis = redis)

@pytest.mark.asyncio(scope="module")
async def test_bit_repository(bit_repository: BitRepository,):
    the_bit = Bit(bytes=int(1).to_bytes(128, byteorder='big'), timestamp=1, source="test_bit_repository")
    await bit_repository.add(the_bit)
    assert the_bit == await bit_repository.get_bit_by_timestamp_and_source(1, "test_bit_repository")