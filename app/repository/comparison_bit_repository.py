from .bit_repository import BitRepository

class ComparisonBitRepository(BitRepository):
    expiration_seconds = 60 * 60 * 25  # 1 days and 1 hour for buffer
    entity_name = "ComparisonBit"