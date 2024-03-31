"""Containers module."""

from dependency_injector import containers, providers
from google.cloud import firestore

from .database import Database, init_redis_pool, init_firestore_client
from .repositories import UserRepository, BitRepository, ComparisonBitRepository, ScoreRepository, PiNotationScoreRepository
from .services import UserService, BitService, TimeService, ComparisonBitService, ScoreService, PiNotationScoreService
from .service.external_request_service import ExternalRequestService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    config = providers.Configuration(yaml_files=["config.yml"])

    redis_pool = providers.Resource(
        init_redis_pool,
        host=config.redis_host,
        password=config.redis_password,
    )

    firestore_db = providers.Singleton(
        init_firestore_client,
        project_id=config.project_id,
    )

    bit_repository = providers.Factory(
        BitRepository,
        redis=redis_pool
    )

    comparison_bit_repository = providers.Factory(
        ComparisonBitRepository,
        redis=redis_pool
    )
    
    score_repository = providers.Factory(
        ScoreRepository,
        redis=redis_pool
    )

    pi_notation_score_repository = providers.Factory(
        PiNotationScoreRepository,
        firestore_db=firestore_db
    )

    time_service = providers.Factory(TimeService)

    external_request_service = providers.Factory(ExternalRequestService)

    bit_service = providers.Factory(
        BitService,
        bit_repository=bit_repository
    )

    comparison_bit_service = providers.Factory(
        ComparisonBitService,
        comparison_bit_repository=comparison_bit_repository
    )

    score_service = providers.Factory(
        ScoreService,
        score_repository=score_repository
    )

    pi_notation_score_service = providers.Factory(
        PiNotationScoreService,
        pi_notation_score_repository=pi_notation_score_repository
    )









    db = providers.Singleton(Database, db_url=config.db.url)

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    

    