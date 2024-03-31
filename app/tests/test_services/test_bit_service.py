import pytest
from fakeredis import FakeAsyncRedis

from app.models import Bit
from app.repository import NotFoundError
from app.repository.bit_repository import BitRepository
from app.service.bit_service import BitService


@pytest.fixture(scope="module")
def redis():
    return FakeAsyncRedis()


@pytest.fixture(scope="module")
def bit_repository(redis):
    return BitRepository(redis=redis)


@pytest.fixture(scope="module")
def bit_service(bit_repository):
    return BitService(bit_repository=bit_repository)


@pytest.mark.asyncio(scope="module")
async def test_bit_service(bit_service: BitService):
    the_bytes = (1).to_bytes(128, byteorder="big")
    the_timestamp = 1
    the_source = "sample_source"

    previous_bit = await bit_service.save_bit(bytes=the_bytes, timestamp=the_timestamp, source=the_source)

    current_bit = await bit_service.save_bit(bytes=the_bytes, timestamp=the_timestamp + 1, source=the_source)

    assert len(the_bytes) == 128  # 1024 bits = 128 bytes
    assert isinstance(current_bit, Bit)
    assert not await bit_service.previous_bit_exists(previous_bit)
    with pytest.raises(NotFoundError):
        await bit_service.get_previous_bit(previous_bit)

    assert await bit_service.previous_bit_exists(current_bit)
    assert previous_bit == await bit_service.get_previous_bit(current_bit)

    with pytest.raises(ValueError, match=r"Incorrect byte length \d+. Correct byte length \d+"):
        await bit_service.save_bit(b"1", the_timestamp, the_source)
