"""Application module."""

from fastapi import FastAPI

from .container import Container
from .endpoints import router


def create_app() -> FastAPI:
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", "password")
    container.config.project_id.from_env("FIRESTORE_PROJECT_ID", "dummy-project-id")

    app = FastAPI()
    app.container = container
    app.include_router(router)
    return app


app = create_app()
