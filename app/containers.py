"""Containers module."""

from dependency_injector import containers, providers

from .database import Database, FirestoreDatabase, init_redis_pool
from .repositories import UserRepository, BitRepository
from .services import UserService, BitService, TimeService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    config = providers.Configuration(yaml_files=["config.yml"])

    redis_pool = providers.Resource(
        init_redis_pool,
        host=config.redis_host,
        password=config.redis_password,
    )

    db = providers.Singleton(Database, db_url=config.db.url)

    firestore_db = providers.Singleton(FirestoreDatabase)



    bit_repository = providers.Factory(
        BitRepository,
        db=firestore_db.provided.client,
    )

    bit_service = providers.Factory(
        BitService,
        bit_repository=bit_repository
    )







    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    

    time_service = providers.Factory(TimeService)