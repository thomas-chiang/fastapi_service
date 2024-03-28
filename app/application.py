"""Application module."""

from fastapi import FastAPI

from .containers import Container
from .endpoints import router


def create_app() -> FastAPI:
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", "password")

    db = container.db()
    db.create_database()

    app = FastAPI()
    app.container = container
    app.include_router(router)
    return app


app = create_app()
