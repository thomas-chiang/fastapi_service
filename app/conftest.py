# import asyncio

# import pytest
# from .application import app
# from fastapi.testclient import TestClient
# from mockfirestore import AsyncMockFirestore
# from app.repositories import PiNotationScoreRepository
# from app.service.external_request_service import ExternalRequestService
# from app.service.bit_service import BitService
# from app.repository.bit_repository import BitRepository
# from app.repository.comparison_bit_repository import ComparisonBitRepository

# from fakeredis import FakeAsyncRedis

# @pytest.fixture(scope="session")
# def client():
#     with TestClient(app=app) as c:
#         yield c


# @pytest.yield_fixture(scope='session')
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

# @pytest.fixture(scope="session")
# def redis():
#     return FakeAsyncRedis()

# @pytest.fixture(scope="session")
# def firestore_db():
#     return AsyncMockFirestore()

# @pytest.fixture(scope="session")
# def bit_repository(redis):
#     return BitRepository(redis = redis)

# @pytest.fixture(scope="session")
# def bit_service(bit_repository):
#     return BitService(bit_repository=bit_repository)

# @pytest.fixture(scope="session")
# def comparison_bit_repository(redis):
#     return ComparisonBitRepository(redis = redis)



# @pytest.fixture(scope="session")
# def pi_notation_score_repository(firestore_db):
#     return PiNotationScoreRepository(firestore_db = firestore_db)

# @pytest.fixture(scope="session")
# def external_request_service():
#     return ExternalRequestService()