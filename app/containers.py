"""Containers module."""

from dependency_injector import containers, providers

from .database import Database, init_redis_pool
from .repositories import UserRepository, BitRepository, ComparisonBitRepository, ScoreRepository
from .services import UserService, BitService, TimeService, ComparisonBitService, ScoreService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    config = providers.Configuration(yaml_files=["config.yml"])

    redis_pool = providers.Resource(
        init_redis_pool,
        host=config.redis_host,
        password=config.redis_password,
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




    db = providers.Singleton(Database, db_url=config.db.url)

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    

    time_service = providers.Factory(TimeService)